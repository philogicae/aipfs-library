import asyncio
from logging import getLogger
from os import getenv
from pathlib import Path

import coloredlogs
from dotenv import load_dotenv

load_dotenv()
coloredlogs.install()
logger = getLogger("ipfs")

from aioipfs import AsyncIPFS


async def add_to_ipfs(
    file_path: str, host: str = getenv("IPFS_HOST", "ipfs-node"), port: int = 5001
) -> str:
    if not Path(file_path).exists():
        logger.error(f"File not found: {file_path}")
        return None

    cids = []
    try:
        client = AsyncIPFS(host=host, port=port)
        logger.info(f"Connecting to IPFS node at {host}:{port}...")

        async with client as ipfs:
            try:
                version = await ipfs.core.version()
                logger.info(f"Connected to IPFS node version: {version['Version']}")
                logger.info(f"Adding file: {file_path}")
                cids = []
                async for added in ipfs.core.add(
                    file_path, quieter=True, recursive=True
                ):
                    cid = added["Hash"]
                    logger.info(f"File added/pinned with CID: {cid}")
                    cids.append(cid)
            except Exception as e:
                logger.info(f"Failed to connect to IPFS node: {str(e)}")
    except Exception as e:
        logger.info(f"Failed to interact with IPFS node: {str(e)}")
        logger.info(f"Error type: {type(e).__name__}")
    return cids


async def main():
    test_file = __file__
    cid = await add_to_ipfs(test_file)
    if cid:
        logger.info(f"https://ipfs.io/ipfs/{cid}")
    else:
        logger.info("\nFailed to add file to IPFS")


if __name__ == "__main__":
    asyncio.run(main())
