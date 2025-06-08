from asyncio import run
from logging import getLogger
from os import getenv
from pathlib import Path
from sys import argv

import coloredlogs
from dotenv import load_dotenv

load_dotenv()
coloredlogs.install()
logger = getLogger("ipfs")

from aioipfs import AsyncIPFS


async def add_to_ipfs(
    file_path: str, host: str = getenv("IPFS_HOST", "ipfs-node"), port: int = 5001
) -> dict[str, str]:
    if not Path(file_path).exists():
        logger.error(f"File not found: {file_path}")
        return {}

    files = {}
    try:
        client = AsyncIPFS(host=host, port=port)
        logger.info(f"Connecting to IPFS node at {host}:{port}...")
        async with client as ipfs:
            logger.info(f"Adding file: {file_path}")
            async for added in ipfs.add(
                file_path, pin=True, recursive=True, quieter=True, no_copy=True
            ):
                curr_hash, curr_name = added["Hash"], added["Name"]
                files[curr_name] = curr_hash
                logger.info(f"File added/pinned: {added}")
            if curr_hash and curr_name:
                try:
                    await ipfs.files.cp(f"/ipfs/{curr_hash}", f"/{curr_name}")
                except:
                    pass
    except Exception as e:
        logger.info(f"Failed to interact with IPFS node: {str(e)}")
    await client.close()
    return files


async def main():
    test_file = argv[1]
    files = await add_to_ipfs(test_file)
    if files:
        for fname, fhash in files.items():
            logger.info(f"{fname}: https://ipfs.io/ipfs/{fhash}")
    else:
        logger.info("\nFailed to add file to IPFS")


if __name__ == "__main__":
    run(main())
