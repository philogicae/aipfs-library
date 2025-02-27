from asyncio import run
from json import dumps, loads
from logging import getLogger
from os import getenv, makedirs, path, walk
from pathlib import Path
from shutil import rmtree
from typing import Any

import coloredlogs
from pydantic import BaseModel, Field

coloredlogs.install()
logger = getLogger("downloader")

from aioipfs import AsyncIPFS
from coinbase_agentkit import ActionProvider, WalletProvider, create_action
from openai import OpenAI
from torrentp import TorrentDownloader

DOWNLOAD_DIR = (
    "/shared/downloads"
    if path.exists("/shared")
    else path.join(
        path.dirname(path.dirname(path.dirname(__file__))), "shared/downloads"
    )
)
makedirs(DOWNLOAD_DIR, exist_ok=True)


async def download_torrent(magnet_link: str):
    await TorrentDownloader(
        magnet_link, DOWNLOAD_DIR, stop_after_download=True
    ).start_download()


def list_all_files() -> list[str]:
    file_paths = []
    for root, _dirs, files in walk(DOWNLOAD_DIR):
        for file in files:
            file_paths.append(path.join(root, file))
    print("Files found:", file_paths)
    return file_paths


class File(BaseModel):
    video_file_path: str
    root_path: str


def get_root_and_file(filename: str, file_list: list[str]) -> tuple[str, str]:
    client = OpenAI(base_url=getenv("GROQ_API_BASE"), api_key=getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model=getenv("GROQ_API_MODEL"),
        messages=[
            {
                "role": "system",
                "content": f"Given a torrent filename and a file list, returns the absolute file path of the best video file match, and also the absolute path of the root (Always starting with /shared/downloads/ + <DIR-OR-FILE>) where the file is located. ALWAYS ONLY respond following STRICTLY the given output JSON schema:\n{dumps(File.model_json_schema()).replace(' ', '').replace('\n', '')}",
            },
            {
                "role": "user",
                "content": f"Find: {filename}\nIn: {file_list}",
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
        stream=False,
    )
    text = response.choices[0].message.content
    data = loads("{" + text.split("{", 1)[1].split("}")[0] + "}")
    root, file = data["root_path"], data["video_file_path"]
    print(f"Root: {root}\nVideo file: {file}")
    return root, file


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


def rm(file_path: str):
    if Path(file_path).exists():
        print(f"Deleting: {file_path}")
        if Path(file_path).is_dir():
            rmtree(file_path)
        else:
            Path(file_path).unlink()


async def download(filename: str, magnet_link: str) -> dict[str, str]:
    await download_torrent(magnet_link)
    file_list = list_all_files()
    root, file = get_root_and_file(filename, file_list)
    files = await add_to_ipfs(file)
    rm(root)
    return (
        {fname: f"https://ipfs.video/gw/{fhash}" for fname, fhash in files.items()}
        if files
        else {}
    )


# TOOL DEFINITION


class DownloadToIPFSSchema(BaseModel):
    filename: str = Field(
        ...,
        description="Filename of the torrent file.",
    )
    magnet_link: str = Field(
        ...,
        description="Magnet link of the torrent file.",
    )


class DownloaderActionProvider(ActionProvider[WalletProvider]):
    def __init__(self):
        super().__init__("downloader-action-provider", [])

    def supports_network(self, *args, **kwargs) -> bool:
        return True

    @create_action(
        name="download-to-ipfs",
        description="""This tool will download a torrent file using the provided filename and magnet link and add it to IPFS, returning a dictionary with the added files' names and links.""",
        schema=DownloadToIPFSSchema,
    )
    def download_to_ipfs(self, args: dict[str, Any]) -> str:
        files = run(download(args["filename"], args["magnet_link"]))
        return f"<download-to-ipfs>{dumps(files)}</download-to-ipfs>"


def downloader_action_provider():
    return DownloaderActionProvider()
