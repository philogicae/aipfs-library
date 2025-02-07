import asyncio
from logging import getLogger
from os import getenv
from pathlib import Path

import coloredlogs
from dotenv import load_dotenv

load_dotenv()
coloredlogs.install()
logger = getLogger("agent")

from aioipfs import AsyncIPFS


async def add_to_ipfs(
    file_path: str, host: str = getenv("IPFS_HOST", "ipfs-node"), port: int = 5001
) -> str:
    if not Path(file_path).is_file():
        logger.info(f"Error: File not found: {file_path}")
        return None

    cid = None
    try:
        client = AsyncIPFS(host=host, port=port)
        logger.info(f"Connecting to IPFS node at {host}:{port}...")

        async with client as ipfs:
            try:
                version = await ipfs.core.version()
                logger.info(f"Connected to IPFS node version: {version['Version']}")
                logger.info(f"Adding file: {file_path}")
                async for added in ipfs.core.add(file_path):
                    cid = added["Hash"]
                    logger.info(f"File added with CID: {cid}")
                    async for _ in ipfs.pin.add(cid):
                        pass
                    logger.info("File pinned successfully")
            except Exception as e:
                logger.info(f"Failed to connect to IPFS node: {str(e)}")
    except Exception as e:
        logger.info(f"Failed to interact with IPFS node: {str(e)}")
        logger.info(f"Error type: {type(e).__name__}")
    return cid


async def main():
    test_file = __file__
    cid = await add_to_ipfs(test_file)
    if cid:
        logger.info(f"https://ipfs.io/ipfs/{cid}")
    else:
        logger.info("\nFailed to add file to IPFS")


if __name__ == "__main__":
    asyncio.run(main())
