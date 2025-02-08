from logging import getLogger
from os import listdir, path
from pathlib import Path

import coloredlogs
from dotenv import load_dotenv

load_dotenv()
coloredlogs.install()
logger = getLogger("agent")

from robyn import ALLOW_CORS, Request, Response, Robyn, status_codes
from robyn.openapi import Components, OpenAPI, OpenAPIInfo
from robyn.types import Body, JSONResponse
from tests.ipfs import add_to_ipfs
from tests.scraper import find_torrents
from tests.torrent import download_torrent


class CompletionRequest(Body):
    prompt: str


class MagnetRequest(Body):
    magnet: str


class PinRequest(Body):
    filename: str


app = Robyn(
    __file__,
    openapi=OpenAPI(
        info=OpenAPIInfo(
            title="AIPFS Library Agent",
            description="Decentralized media library managed by AI agents indexing torrents and curated by the community",
            version="1.0.0",
            components=Components(),
        ),
    ),
)
ALLOW_CORS(app, origins=["*"])

ROOT = Path(__file__).parent.resolve()


async def startup():
    logger.info("Starting up...")
    # ...
    logger.info("Ready!")


app.startup_handler(startup)


@app.before_request()
async def log_request(request: Request):
    logger.info(f"{request.method}: {request.url.path}")
    return request


@app.after_request()
async def log_response(response: Response):
    logger.info(f"{response.response_type.upper()}: {response.status_code}")
    return response


@app.options("/v1/chat/completions")
@app.post("/v1/chat/completions")
async def completion(request: Request, _: CompletionRequest):
    if request.method == "OPTIONS":
        return Response(
            status_code=status_codes.HTTP_200_OK, headers={}, description="OK"
        )
    prompt = request.json().get("prompt")
    torrents = await find_torrents(prompt)
    return JSONResponse(result=torrents)


@app.options("/v1/download")
@app.post("/v1/download")
async def download(request: Request, _: MagnetRequest):
    if request.method == "OPTIONS":
        return Response(
            status_code=status_codes.HTTP_200_OK, headers={}, description="OK"
        )
    magnet = request.json().get("magnet")
    await download_torrent(magnet)
    return JSONResponse({"result": "OK"})


@app.options("/v1/pin")
@app.post("/v1/pin")
async def pin(request: Request, _: PinRequest):
    if request.method == "OPTIONS":
        return Response(
            status_code=status_codes.HTTP_200_OK, headers={}, description="OK"
        )
    filename = request.json().get("filename")
    download_dir = "/shared/downloads"
    file_path = path.join(download_dir, filename)
    if not path.exists(file_path):
        return JSONResponse(
            status_code=status_codes.HTTP_400_BAD_REQUEST,
            headers={},
            description="File not found",
        )
    cids = await add_to_ipfs(file_path)
    if cids:
        return JSONResponse(
            status_code=status_codes.HTTP_200_OK,
            headers={},
            description={
                "cids": cids,
                "urls": [f"https://ipfs.io/ipfs/{cid}" for cid in cids],
            },
        )
    return JSONResponse(
        status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR,
        headers={},
        description="Error",
    )


@app.get("/v1/files")
async def list_files():
    download_dir = "/shared/downloads"
    try:
        return JSONResponse({"files": listdir(download_dir)})
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return Response(
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={},
            description=f"Error listing files: {str(e)}",
        )


if __name__ == "__main__":
    app.start(host="0.0.0.0", port=1789)
