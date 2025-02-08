import asyncio
import sys
from logging import getLogger
from os import makedirs

import coloredlogs
from torrentp import TorrentDownloader

coloredlogs.install()
logger = getLogger("torrent")

download_dir = "/shared/downloads"
makedirs(download_dir, exist_ok=True)


async def download_torrent(magnet_link: str):
    await TorrentDownloader(
        magnet_link, download_dir, stop_after_download=True
    ).start_download()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error("Usage: python src/tests/torrent.py <search>")
        exit(1)
    asyncio.run(download_torrent(sys.argv[1]))
