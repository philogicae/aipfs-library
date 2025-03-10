from asyncio import run
from json import dumps, loads
from logging import getLogger
from os import getenv
from re import sub
from time import time
from typing import Any, List, Optional
from urllib.parse import quote

import coloredlogs
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()
coloredlogs.install()
logger = getLogger("scraper")


from coinbase_agentkit import ActionProvider, WalletProvider, create_action
from crawl4ai import AsyncWebCrawler, CacheMode
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from openai import OpenAI

FILTERS = {
    "full_links": r"(http|https|ftp):[/]{1,2}[a-zA-Z0-9.]+[a-zA-Z0-9./?=+~_\-@:%#&]*",
    "backslashes": r"\\",
    "local_links": r"(a href=)*(<|\")\/[a-zA-Z0-9./?=+~()_\-@:%#&]*(>|\")* *",
    "some_texts": r' *"[a-zA-Z ]+" *',
    "empty_angle_brackets": r" *< *> *",
    "empty_curly_brackets": r" *\{ *\} *",
    "empty_parenthesis": r" *\( *\) *",
    "empty_brackets": r" *\[ *\] *",
    "tags": r"(>?<(img|a) ((alt|src)=)+)|(<a href=)",
    "date": r'<label title=("[a-zA-Z0-9()+: ]+"|>)',
}

REPLACERS = {
    "spans": [r"</?span>", " | "],
    "weird spaced bars": [r" *\|[ \|]+", " | "],
    "double_quotes": [r'"[" ]+', ""],
    "single_angle_bracket": [r"<|>", ""],
}

WEBSITES = {
    "thepiratebay.org": dict(
        search="https://thepiratebay.org/search.php?q={query}",
        parsing="html",
        exclude_patterns=[],
    ),
    "nyaa.si": dict(
        search="https://nyaa.si/?f=0&c=0_0&q={query}&s=seeders&o=desc",
        parsing="markdown",
        exclude_patterns=["local_links"],
    ),
}

MODELS = dict(
    groq=dict(
        api_url=getenv("GROQ_API_BASE"),
        api_token=getenv("GROQ_API_KEY"),
        model=getenv("GROQ_API_MODEL_SCRAPER"),
    ),
    hyperbolic=dict(
        api_url=getenv("HYPERBOLIC_API_BASE"),
        api_token=getenv("HYPERBOLIC_API_KEY"),
        model=getenv("HYPERBOLIC_API_MODEL"),
    ),
)

PARAMS = dict(temperature=0.1, stream=False)


class Torrent(BaseModel):
    filename: str
    date: str
    size: str
    magnet_link: str
    seeders: int
    leechers: int
    uploader: str
    website_source: str


class Results(BaseModel):
    torrents: List[Torrent]


def shrink_text(
    text: str, exclude_patterns: Optional[List[str]] = None, max_chars=5000
) -> str:
    text = text.split("<li>", 1)[-1].replace("<li>", "")
    for name, pattern in FILTERS.items():
        if exclude_patterns and name in exclude_patterns:
            continue
        text = sub(pattern, "", text)
    for name, replacer in REPLACERS.items():
        if exclude_patterns and name in exclude_patterns:
            continue
        text = sub(replacer[0], replacer[1], text)
    truncated = text[:max_chars]
    return sub(r"\n+", "\n", "\n".join(truncated.split("\n")[:-1])).strip()


async def scrape_torrents(query: str, sources: Optional[List[str]] = None) -> str:
    browser_config = BrowserConfig(
        browser_type="chromium",
        headless=True,
        text_mode=True,
        light_mode=True,
    )
    md_generator = DefaultMarkdownGenerator(
        options=dict(
            ignore_images=True,
            ignore_links=False,
            skip_internal_links=True,
            escape_html=True,
        )
    )
    run_config = CrawlerRunConfig(
        markdown_generator=md_generator,
        remove_overlay_elements=True,
        exclude_social_media_links=True,
        excluded_tags=["header", "footer", "nav"],
        remove_forms=True,
        cache_mode=CacheMode.DISABLED,
    )

    results = ""
    async with AsyncWebCrawler(
        config=browser_config, always_bypass_cache=True
    ) as crawler:
        for source, data in WEBSITES.items():
            if sources is None or source in sources:
                url = data["search"].format(query=quote(query))
                result = await crawler.arun(url=url, config=run_config)
                result = shrink_text(
                    (
                        result.cleaned_html
                        if data["parsing"] == "html"
                        else result.markdown
                    ),
                    data["exclude_patterns"],
                )
                results += (
                    f"\nSCRAPING WEBSITE SOURCE -> {source}:\n{result}\n----------"
                )
    return results


def extract_results(text: str, llm: Optional[str] = None) -> str:
    if llm is None:
        llm = "groq"

    client = OpenAI(
        base_url=MODELS[llm]["api_url"],
        api_key=MODELS[llm]["api_token"],
    )
    response = client.chat.completions.create(
        model=MODELS[llm]["model"],
        messages=[
            {
                "role": "system",
                "content": f"Always extract every single torrent objects found in the provided scraped data. NEVER truncate magnet links. If no match, torrent list must be empty. ALWAYS ONLY respond following STRICTLY the given output JSON schema:\n{dumps(Results.model_json_schema()).replace(' ', '').replace('\n', '')}",
            },
            {
                "role": "user",
                "content": text,
            },
        ],
        response_format={"type": "json_object"},
        **PARAMS,
    )
    return response.choices[0].message.content


def extract_json(text: str) -> List[dict]:
    return loads("[" + "]".join(text.split("[", 1)[1].split("]")[:-1]) + "]")


def filtering_results(torrents: dict, min_peers=0, max_items=20) -> List[dict]:
    return list(
        sorted(
            filter(
                lambda torrent: int(torrent["seeders"]) + int(torrent["leechers"])
                >= min_peers,
                torrents,
            ),
            key=lambda torrent: int(torrent["seeders"]) + int(torrent["leechers"]),
            reverse=True,
        )
    )[:max_items]


async def find_torrent_list(
    query: str,
    sources: Optional[List[str]] = None,
    llm: Optional[str] = None,
    max_retries=3,
) -> List[dict]:
    start_time = time()
    results = await scrape_torrents(query, sources=sources)
    retries, extracted = 0, ""
    while retries < max_retries:
        try:
            extracted = extract_results(results, llm=llm)
            extracted = extract_json(extracted)
            extracted = filtering_results(extracted)
            logger.info(f"Completed in {time() - start_time:.2f} sec.")
            return extracted
        except Exception as e:
            logger.error(e)
            retries += 1
            if retries >= max_retries:
                logger.error("Max retries reached.")
                logger.info(f"Failed in {time() - start_time:.2f} sec.")
    return []


# TOOL DEFINITION


class SearchTorrentsSchema(BaseModel):
    keywords: str = Field(
        ...,
        description="Space-separated keywords to search torrents for. Keywords used by users should be preserved.",
    )


class ScraperActionProvider(ActionProvider[WalletProvider]):
    def __init__(self):
        super().__init__("scraper-action-provider", [])

    def supports_network(self, *args, **kwargs) -> bool:
        return True

    @create_action(
        name="search-torrents",
        description="""This tool will search for torrents using the provided space-separated keywords and return a list of found torrents. Results should NEVER be repeated by the agent afterwards, because this tool output is always visible for the user, but you should reply to signal the search success or failure and recommend the best file to choose from the list, following those specs ordered by priority: greater number of seeds, 1080p resolution minimum, smaller file size, and avoid x265 encoding (too compute intensive on a streaming device). If the results seem to be too heterogeneous, recommend to narrow down the search by asking additional keywords. Comply to user's request and keep your answer short.""",
        schema=SearchTorrentsSchema,
    )
    def search_torrents(self, args: dict[str, Any]) -> str:
        torrents = run(find_torrent_list(args["keywords"]))
        if not torrents:
            logger.error("No result found.")
        return f'<tool-search-torrents>{{"torrents": {dumps(torrents)}}}</tool-search-torrents>'


def scraper_action_provider():
    return ScraperActionProvider()
