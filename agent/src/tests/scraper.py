import sys
from asyncio import run
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from typing import List, Optional

from rich import print
from rich.console import Console
from rich.table import Table

from src.tools.scraper import find_torrent_list


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
    table.add_column("Source", style="yellow")

    for i, result in enumerate(results):
        table.add_row(
            str(i + 1),
            result["filename"],
            result["size"],
            str(result["seeders"]),
            str(result["leechers"]),
            result["date"],
            result["uploader"],
            result["website_source"],
        )
    console.print(table)


async def search(
    text: str, sources: Optional[List[str]] = None, llm: Optional[str] = None
):
    torrents = await find_torrent_list(query=text, sources=sources, llm=llm)
    if not torrents:
        print("No result found.")
    else:
        display_torrents(torrents)
        while True:
            text = input("Index ('x' to quit): ")
            try:
                index = int(text) - 1
                print(torrents[index])
            except Exception:
                return


def get_query():
    return " ".join(sys.argv[1:])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/tests/scraper.py <search>")
        exit(1)
    run(search(get_query()))
