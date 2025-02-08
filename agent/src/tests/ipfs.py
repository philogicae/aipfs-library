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

    files = []
    try:
        client = AsyncIPFS(host=host, port=port)
        logger.info(f"Connecting to IPFS node at {host}:{port}...")
        async with client as ipfs:
            try:
                logger.info(f"Adding file: {file_path}")
                files = {}
                async for added in ipfs.core.add(
                    file_path, pin=True, recursive=True, quieter=True
                ):
                    logger.info(f"File added/pinned: {added}")
                    files[added["Name"]] = added["Hash"]
            except Exception as e:
                logger.info(f"Failed to connect to IPFS node: {str(e)}")
    except Exception as e:
        logger.info(f"Failed to interact with IPFS node: {str(e)}")
        logger.info(f"Error type: {type(e).__name__}")
    return files


async def main():
    test_file = __file__
    files = await add_to_ipfs(test_file)
    if files:
        for file in files:
            logger.info(f"{file['Name']}: https://ipfs.io/ipfs/{file['Hash']}")
    else:
        logger.info("\nFailed to add file to IPFS")


if __name__ == "__main__":
    asyncio.run(main())
