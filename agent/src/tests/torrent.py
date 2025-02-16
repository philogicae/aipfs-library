import asyncio
import sys
from logging import getLogger
from os import makedirs

import coloredlogs
from torrentp import TorrentDownloader

coloredlogs.install()
logger = getLogger("torrent")

DOWNLOAD_DIR = "/shared/downloads"
makedirs(DOWNLOAD_DIR, exist_ok=True)


async def download_torrent(magnet_link: str):
    await TorrentDownloader(
        magnet_link, DOWNLOAD_DIR, stop_after_download=True
    ).start_download()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error("Usage: python src/tests/torrent.py <magnet_link>")
        exit(1)
    asyncio.run(download_torrent(sys.argv[1]))
