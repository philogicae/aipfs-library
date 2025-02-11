import asyncio
import re
import time
from json import dumps, loads
from logging import getLogger
from os import getenv
from typing import List, Optional
from urllib.parse import quote

import coloredlogs
from cdp_langchain.tools import CdpTool
from cdp_langchain.utils import CdpAgentkitWrapper
from crawl4ai import AsyncWebCrawler, CacheMode
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()
coloredlogs.install()
logger = getLogger("scraper")

FILTERS = {
    "full_links": r"(http|https|ftp):[/]{1,2}[a-zA-Z0-9.]+[a-zA-Z0-9./?=+~_\-@:%#&]*",
    "backslashes": r"\\",
    "local_links": r"<\/[a-zA-Z0-9./?=+~()_\-@:%#&]*> *",
    "some_texts": r' *"[a-zA-Z ]+" *',
    "empty_angle_brackets": r" *< *> *",
    "empty_curly_brackets": r" *\{ *\} *",
    "empty_parenthesis": r" *\( *\) *",
    "empty_brackets": r" *\[ *\] *",
}

WEBSITES = {
    "thepiratebay.org": dict(
        search="https://www2.thepiratebay3.to/s/?q={query}", exclude_patterns=[]
    ),
    "nyaa.si": dict(
        search="https://nyaa.si/?f=0&c=0_0&q={query}&s=seeders&o=desc",
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

PARAMS = dict(temperature=0.2, stream=False)


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
    text: str, exclude_patterns: Optional[List[str]] = None, max_chars=10000
) -> str:
    for name, pattern in FILTERS.items():
        if exclude_patterns and name in exclude_patterns:
            continue
        text = re.sub(pattern, "", text)
    truncated = text[:max_chars]
    return "\n".join(truncated.split("\n")[:-1])


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
                result = shrink_text(result.markdown, data["exclude_patterns"])
                results += f"\nFOR WEBSITE SOURCE -> {source}:\n{result}\n----------"
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
                "content": f"Extract ALL torrent objects from the provided data without filtering. NEVER truncate magnet links. If no match, torrent list must be empty. ALWAYS ONLY respond following STRICTLY the given output JSON schema:\n{dumps(Results.model_json_schema()).replace(' ', '').replace('\n', '')}",
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


def filtering_results(torrents: dict, min_peers=0) -> List[dict]:
    return list(
        sorted(
            filter(
                lambda torrent: torrent["seeders"] + torrent["leechers"] >= min_peers,
                torrents,
            ),
            key=lambda torrent: torrent["seeders"] + torrent["leechers"],
            reverse=True,
        )
    )


async def find_torrent_list(
    query: str,
    sources: Optional[List[str]] = None,
    llm: Optional[str] = None,
    max_retries=2,
) -> List[dict]:
    start_time = time.time()
    results = await scrape_torrents(query, sources=sources)
    retries, extracted = 0, ""
    while retries < max_retries:
        try:
            extracted = extract_results(results, llm=llm)
            extracted = extract_json(extracted)
            extracted = filtering_results(extracted)
            logger.info(f"Completed in {time.time() - start_time:.2f} sec.")
            return extracted
        except Exception as e:
            logger.error(e)
            retries += 1
            if retries >= max_retries:
                logger.error("Max retries reached.")
                logger.info(f"Failed in {time.time() - start_time:.2f} sec.")
    return []


# TOOL DEFINITION

SEARCH_TORRENTS_PROMPT = """
This tool will search for torrents using the provided query and return a list of found torrents. Results should NEVER be repeated by the agent afterwards, because this tool output is always visible for the user, but you should reply to signal the search success or failure and recommend the best file to choose from the list, following those specs ordered by priority: greater number of seeds, 1080p resolution minimum, smaller file size, and avoid x265 encoding (too compute intensive on a streaming device). If the results seem to be too heterogeneous, recommend to narrow down the search by asking additional keywords. Keep your answer short.
"""


def search_torrents(query: str) -> str:
    """Search for torrents using the provided query.

    Args:
        query (str): The query to search torrents for.

    Returns:
        str: The list of found torrents.

    """

    torrents = asyncio.run(find_torrent_list(query))
    if not torrents:
        logger.error("No result found.")
    return f'<tool-search-torrents>{{"torrents": {dumps(torrents)}}}</tool-search-torrents>'


class SearchTorrentsInput(BaseModel):
    """Input argument schema for search torrents action."""

    query: str = Field(
        ...,
        description="The query to search torrents for. Keywords used by users in their queries should be preserved.",
    )


def search_torrents_tool(agentkit: CdpAgentkitWrapper):
    return CdpTool(
        cdp_agentkit_wrapper=agentkit,
        name="search_torrents",
        description=SEARCH_TORRENTS_PROMPT,
        func=search_torrents,
        args_schema=SearchTorrentsInput,
    )
