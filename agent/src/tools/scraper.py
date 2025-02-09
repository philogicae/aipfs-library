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
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()
coloredlogs.install()
logger = getLogger("scraper")

WEBSITES = {
    "thepiratebay10.info": dict(
        search="https://thepiratebay10.info/search/{query}/1/99/0",
        filter=r"<?https:/{1,2}thepiratebay10\.info[a-zA-Z0-9\-.\/\?_=\&%]*>?",
    )
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

PARAMS = dict(temperature=0.7, stream=False)


def to_safe_url(text: str):
    return quote(text)


def extract_json(text: str):
    return loads("[" + "]".join(text.split("[", 1)[1].split("]")[:-1]) + "]")


class Torrent(BaseModel):
    filename: str
    date: str
    size: str
    magnet_link: str
    seeders: int
    leechers: int
    uploader: str


class Results(BaseModel):
    torrents: List[Torrent]


async def scrape(query: str, source: Optional[str] = None, max_chars=10000):
    if source is None:
        source = "thepiratebay10.info"

    browser_config = BrowserConfig()
    run_config = CrawlerRunConfig()

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=WEBSITES[source]["search"].format(query=to_safe_url(query)),
            config=run_config,
        )
        result = re.sub(
            WEBSITES[source]["filter"],
            "",
            result.markdown,
        )
        truncated = result[:max_chars]
        truncated = "\n".join(truncated.split("\n")[:-1])
        return truncated


def extract(text: str, llm: Optional[str] = None):
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
                "content": f"Extract all torrent objects from the provided markdown content. NEVER truncate any magnet link. If no match, torrent list must be empty. ALWAYS ONLY respond following STRICTLY the given output JSON schema and by enforcing the double quote standard to make it valid and parseable:\n{dumps(Results.model_json_schema())}",
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


async def find_torrent_list(
    query: str, source: Optional[str] = None, llm: Optional[str] = None, max_retries=1
):
    start_time = time.time()
    results = await scrape(query, source=source)

    retries, extracted = 0, ""
    while retries < max_retries:
        try:
            extracted = extract(results, llm=llm)
            extracted = extract_json(extracted)
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
This tool will search for torrents using the provided query and return a list of found torrents. Results should never be displayed by the agent afterwards, since this tool output is always visible by the user. The agent can reply to signal the search success or failure.
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
        description="The query to search torrents for. e.g. `lord of the rings ebook`. Keywords used by users in their queries should be preserved.",
    )


def search_torrents_tool(agentkit: CdpAgentkitWrapper):
    return CdpTool(
        cdp_agentkit_wrapper=agentkit,
        name="search_torrents",
        description=SEARCH_TORRENTS_PROMPT,
        func=search_torrents,
        args_schema=SearchTorrentsInput,
    )
