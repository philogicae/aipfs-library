import asyncio
import re
import sys
import time
from json import loads
from logging import getLogger
from os import getenv
from typing import List, Optional
from urllib.parse import quote

import coloredlogs
import openai
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from dotenv import load_dotenv
from pydantic import BaseModel
from rich import print
from rich.console import Console
from rich.table import Table

load_dotenv()
coloredlogs.install()
logger = getLogger("scraper")

SOURCES = {
    "thepiratebay10.info": dict(
        search="https://thepiratebay10.info/search/{query}/1/99/0",
        filter=r"<?https:/{1,2}thepiratebay10\.info[a-zA-Z0-9\-.\/\?_=\&%]*>?",
    )
}

MODELS = dict(
    groq=dict(
        api_url=getenv("OPENAI_API_BASE"),
        api_token=getenv("OPENAI_API_KEY"),
        model=getenv("OPENAI_API_MODEL"),
    ),
    hyperbolic=dict(
        api_url=getenv("HYPERBOLIC_API_BASE"),
        api_token=getenv("HYPERBOLIC_API_KEY"),
        model=getenv("HYPERBOLIC_API_MODEL"),
    ),
)

PARAMS = dict(temperature=0.7, stream=False)


def get_query():
    return " ".join(sys.argv[1:])


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


async def find(query: str, source: Optional[str] = None, max_chars=10000):
    if source is None:
        source = "thepiratebay10.info"

    browser_config = BrowserConfig()
    run_config = CrawlerRunConfig()

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=SOURCES[source]["search"].format(query=to_safe_url(query)),
            config=run_config,
        )
        result = re.sub(
            SOURCES[source]["filter"],
            "",
            result.markdown,
        )
        truncated = result[:max_chars]
        truncated = "\n".join(truncated.split("\n")[:-1])
        return truncated


def extract(text: str, llm: Optional[str] = None):
    if llm is None:
        llm = "groq"

    client = openai.OpenAI(
        base_url=MODELS[llm]["api_url"],
        api_key=MODELS[llm]["api_token"],
    )
    response = client.chat.completions.create(
        model=MODELS[llm]["model"],
        messages=[
            {
                "role": "system",
                "content": f"Extract all torrent objects from the provided content. Never truncate any magnet link. Always respond following the given output JSON schema using proper double quotes:\n{Results.model_json_schema()}",
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


async def find_torrents(
    query: str, source: Optional[str] = None, llm: Optional[str] = None
):
    start_time = time.time()
    results = await find(query, source=source)

    max_retries, retries, extracted = 3, 0, ""
    while retries < max_retries:
        try:
            extracted = extract(results, llm=llm)
            extracted = extract_json(extracted)
            logger.info(f"Completed in {time.time() - start_time:.2f} sec.")
            return extracted
        except Exception as e:
            print(extracted)
            logger.error(e)
            retries += 1
            if retries >= max_retries:
                logger.error("Max retries reached.")
                logger.info(f"Failed in {time.time() - start_time:.2f} sec.")
    return []


def display_torrents(results):
    console = Console()
    table = Table(title="Torrents")
    table.add_column("#", style="cyan", no_wrap=True)
    table.add_column("Filename", style="magenta")
    table.add_column("Size", justify="right", style="green")
    table.add_column("SE", justify="right", style="green")
    table.add_column("LE", justify="right", style="green")
    table.add_column("Date", style="bright_cyan")
    table.add_column("Uploader", style="blue")

    for i, result in enumerate(results):
        table.add_row(
            str(i + 1),
            result["filename"],
            result["size"],
            str(result["seeders"]),
            str(result["leechers"]),
            result["date"],
            result["uploader"],
        )
    console.print(table)


async def search(text: str, source: Optional[str] = None, llm: Optional[str] = None):
    torrents = await find_torrents(query=text, source=source, llm=llm)
    if not torrents:
        logger.error("No results found.")
    else:
        display_torrents(torrents)
        while True:
            text = input("Index ('x' to quit): ")
            try:
                index = int(text) - 1
                print(torrents[index])
            except Exception:
                return


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Usage: python src/tests/scraper.py <search>")
        exit(1)
    asyncio.run(search(get_query()))
