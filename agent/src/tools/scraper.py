import re
from asyncio import run
from json import dumps, loads
from logging import getLogger
from os import getenv
from time import time
from typing import Any
from urllib.parse import quote

import coloredlogs
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

load_dotenv()
coloredlogs.install()
logger = getLogger("scraper")


from coinbase_agentkit import ActionProvider, WalletProvider, create_action
from crawl4ai import AsyncWebCrawler, CacheMode
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from openai import OpenAI

# Module-level configurations for AsyncWebCrawler
BROWSER_CONFIG = BrowserConfig(
    browser_type="chromium",
    headless=True,
    text_mode=True,
    light_mode=True,
)
DEFAULT_MD_GENERATOR = DefaultMarkdownGenerator(
    options=dict(
        ignore_images=True,
        ignore_links=False,
        skip_internal_links=True,
        escape_html=True,
    )
)
DEFAULT_CRAWLER_RUN_CONFIG = CrawlerRunConfig(
    markdown_generator=DEFAULT_MD_GENERATOR,
    remove_overlay_elements=True,
    exclude_social_media_links=True,
    excluded_tags=["header", "footer", "nav"],
    remove_forms=True,
    cache_mode=CacheMode.DISABLED,
)


FILTERS = {
    "full_links": re.compile(
        r"(http|https|ftp):[/]{1,2}[a-zA-Z0-9.]+[a-zA-Z0-9./?=+~_\-@:%#&]*"
    ),
    "backslashes": re.compile(r"\\"),
    "local_links": re.compile(
        r"(a href=)*(<|\")\/[a-zA-Z0-9./?=+~()_\-@:%#&]*(>|\")* *"
    ),
    "some_texts": re.compile(r' *"[a-zA-Z ]+" *'),
    "empty_angle_brackets": re.compile(r" *< *> *"),
    "empty_curly_brackets": re.compile(r" *\{ *\} *"),
    "empty_parenthesis": re.compile(r" *\( *\) *"),
    "empty_brackets": re.compile(r" *\[ *\] *"),
    "tags": re.compile(r"(>?<(img|a) ((alt|src)=)+)|(<a href=\")"),
    "date": re.compile(r'<label title=("[a-zA-Z0-9()+: ]+"|>)'),
}

REPLACERS = {
    "weird_spaces": [re.compile(r"\u00A0"), " "],
    "spans": [re.compile(r"</?span>"), " | "],
    "weird spaced bars": [re.compile(r" *\|[ \|]+"), " | "],
    "double_quotes": [re.compile(r'"[" ]+'), ""],
    "single_angle_bracket": [re.compile(r"<|>"), ""],
    "thepiratebay_labels": [
        re.compile(r"Category.*?ULed by", re.DOTALL),
        "category | filename | date | link | size | seeders | leechers | uploader",
    ],
    "thepiratebay_magnet_fix": [
        re.compile(r"announce\|"),
        "announce |",
    ],
    "nyaa_remove_click_here_line": [
        re.compile(r"^\[Click here.*?\]\n"),
        "",
    ],
    "nyaa_header_block": [
        re.compile(r"Category \| Name \| Link \|Size \|Date \|\s*\r?\n[\|-]+\s*\r?\n"),
        "category | filename | link | size | date | seeders | leechers | downloads\n",
    ],
    "nyaa_remove_comments": [
        re.compile(r"\| \[ \d+\]\( \"\d+ comments\"\) "),
        "| ",
    ],
    "nyaa_clean_category_and_name_column_data": [
        re.compile(r'([\|\n])[^\|\n]+\"([^"\|]+)\"[^\|]+'),
        r"\1 \2 ",
    ],
    "nyaa_clean_link_column_data": [
        re.compile(r"\|\((magnet:\?[^)]+)\)"),
        r"| \1",
    ],
    "gt": [re.compile("&gt;"), " -"],
    "amp": [re.compile("&amp;"), "&"],
    "bad_starting_spaced_bars": [re.compile(r"\n[\| ]+"), "\n"],
    "bad_ending_spaces": [re.compile(r" +\n"), "\n"],
    "duplicated_spaces": [re.compile(r" {2,4}"), " "],
    "size": [re.compile(r"([\d.]+[\s ]?[KMG])i?B"), r"\1B"],
    "to_csv": [re.compile(r" \| *"), ";"],
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
    gemini=dict(
        api_url=getenv("GEMINI_API_BASE"),
        api_token=getenv("GEMINI_API_KEY"),
        model=getenv("GEMINI_API_MODEL"),
    ),
)

PARAMS = dict(temperature=0.1, stream=False)


class Torrent(BaseModel):
    filename: str
    category: str | None = None
    date: str
    size: str
    magnet_link: str | None = None
    seeders: int
    leechers: int
    downloads: int | None = None
    uploader: str | None = None
    website_source: str


class Results(BaseModel):
    torrents: list[Torrent]


def shrink_text(
    text: str, exclude_patterns: list[str] | None = None, max_chars=5000
) -> str:
    text = text.split("<li>", 1)[-1].replace("<li>", "")
    for name, pattern in FILTERS.items():
        if exclude_patterns and name in exclude_patterns:
            continue
        text = pattern.sub("", text)
    for name, replacer_config in REPLACERS.items():
        if exclude_patterns and name in exclude_patterns:
            continue
        pattern, replacement_str = replacer_config
        text = pattern.sub(replacement_str, text)
    if len(text) > max_chars:
        safe_truncate_pos = text.rfind("\n", 0, max_chars)
        if safe_truncate_pos == -1:
            text = text[:max_chars]
        else:
            text = text[:safe_truncate_pos]
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


async def scrape_torrents(query: str, sources: list[str] | None = None) -> str:
    results_list = []
    async with AsyncWebCrawler(
        config=BROWSER_CONFIG, always_bypass_cache=True
    ) as crawler:
        for source, data in WEBSITES.items():
            if sources is None or source in sources:
                url = data["search"].format(query=quote(query))
                try:
                    crawl_result = await crawler.arun(
                        url=url, config=DEFAULT_CRAWLER_RUN_CONFIG
                    )
                    processed_text = shrink_text(
                        (
                            crawl_result.cleaned_html
                            if data["parsing"] == "html"
                            else crawl_result.markdown
                        ),
                        data.get("exclude_patterns", []),
                    )
                    results_list.append(
                        f"SCRAPING WEBSITE SOURCE -> {source}:\n{processed_text}"
                    )
                except Exception as e:
                    logger.error(
                        f"Error scraping {source} for query '{query}' at {url}: {e}"
                    )
                    results_list.append(
                        f"ERROR SCRAPING WEBSITE SOURCE -> {source}: {e}"
                    )
    return "\n----------\n".join(results_list)


def extract_results_with_llm(text: str, llm: str) -> str:
    client = OpenAI(
        base_url=MODELS[llm]["api_url"],
        api_key=MODELS[llm]["api_token"],
    )
    response = client.chat.completions.create(
        model=MODELS[llm]["model"],
        messages=[
            {
                "role": "system",
                "content": (
                    "Always extract every single torrent objects found "
                    "in the provided scraped data. "
                    "NEVER truncate magnet links. If no match, torrent list must be empty. "
                    "ALWAYS ONLY respond following STRICTLY the given output JSON schema:\n"
                    f"{dumps(Results.model_json_schema()).replace(' ', '').replace('\n', '')}"
                ),
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


def extract_json_after_llm(text: str) -> list[dict]:
    return loads("[" + "]".join(text.split("[", 1)[1].split("]")[:-1]) + "]")


def extract_with_llm(text: str, llm: str | None) -> list[dict]:
    if not llm:
        logger.info("No LLM specified, skipping extraction.")
        return []
    return extract_json_after_llm(extract_results_with_llm(text, llm=llm))


def extract_via_csv(text: str) -> list[dict]:
    by_source = text.split("\n----------\n")
    torrents = []
    for data in by_source:
        source, content = data.split("\n", 1)
        if "No results" in content:
            continue
        source = source.split("-> ", 1)[1][:-1]
        content = content.splitlines()
        headers = content[0].split(";")
        for line in content[1:]:
            row = line.split(";")
            torrent = dict(zip(headers, row))
            torrent["website_source"] = source
            try:
                Torrent.model_validate(torrent)
            except ValidationError:
                continue
            torrents.append(torrent)
    return torrents


def filtering_results(torrents: dict, min_peers=0, max_items=20) -> list[dict]:
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
    sources: list[str] | None = None,
    llm: str | None = None,
    max_retries=3,
) -> list[dict]:
    start_time = time()
    results = await scrape_torrents(query, sources=sources)
    retries = 0
    while retries < max_retries:
        try:
            extracted_data = None
            if llm:
                extracted_data = extract_with_llm(results, llm=llm)
            else:
                extracted_data = extract_via_csv(results)
            extracted_data = filtering_results(extracted_data)
            logger.info(
                f"Successfully extracted results in {time() - start_time:.2f} sec."
            )
            return extracted_data
        except Exception as e:
            retries += 1
            logger.error(
                f"Attempt {retries}/{max_retries} failed to extract results: {e}"
            )
            if retries >= max_retries:
                logger.error("Max retries reached. Failed to extract results.")
                logger.info(
                    f"Total time taken before failure: {time() - start_time:.2f} sec."
                )
    logger.warning(
        f"Exhausted all {max_retries} retries. "
        f"Returning empty list. Total time: {time() - start_time:.2f} sec."
    )
    return []


# TOOL DEFINITION


class SearchTorrentsSchema(BaseModel):
    keywords: str = Field(
        ...,
        description=(
            "Space-separated keywords to search torrents for. "
            "Keywords used by users should be preserved."
        ),
    )


class ScraperActionProvider(ActionProvider[WalletProvider]):
    def __init__(self):
        super().__init__("scraper-action-provider", [])

    def supports_network(self, *_args, **_kwargs) -> bool:
        return True

    @create_action(
        name="search-torrents",
        description=(
            "This tool will search for torrents using the provided space-separated keywords "
            "and return a list of found torrents. Results should NEVER be repeated by the agent "
            "afterwards, because this tool output is always visible for the user, but you should "
            "reply to signal the search success or failure and recommend the best file to choose "
            "from the list, following those specs ordered by priority: greater number of seeds, "
            "1080p resolution minimum, smaller file size, and avoid x265 encoding (too compute "
            "intensive on a streaming device). If the results seem to be too heterogeneous, "
            "recommend to narrow down the search by asking additional keywords. Comply to user's "
            "request and keep your answer short."
        ),
        schema=SearchTorrentsSchema,
    )
    def search_torrents(self, _args: dict[str, Any]) -> str:
        torrents = run(find_torrent_list(_args["keywords"]))
        if not torrents:
            logger.error("No result found.")
        return f'<tool-search-torrents>{{"torrents": {dumps(torrents)}}}</tool-search-torrents>'


def scraper_action_provider():
    return ScraperActionProvider()
