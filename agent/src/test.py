from logging import getLogger
from os import listdir, makedirs, path
from pathlib import Path
from shutil import rmtree

import coloredlogs
from dotenv import load_dotenv

load_dotenv()
coloredlogs.install()
logger = getLogger("agent")

from robyn import ALLOW_CORS, Request, Response, Robyn, status_codes
from robyn.openapi import Components, OpenAPI, OpenAPIInfo
from robyn.types import Body, JSONResponse
from tests.ipfs import add_to_ipfs
from tests.scraper import find_torrent_list
from tests.torrent import download_torrent


class CompletionRequest(Body):
    prompt: str


class MagnetRequest(Body):
    magnet: str


class FileRequest(Body):
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

DOWNLOAD_DIR = (
    "/shared/downloads"
    if path.exists("/shared")
    else path.join(path.dirname(path.dirname(__file__)), "shared/downloads")
)
makedirs(DOWNLOAD_DIR, exist_ok=True)


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


@app.options("/v1/scrape")
@app.post("/v1/scrape")
async def scrape(request: Request, _: CompletionRequest):
    if request.method == "OPTIONS":
        return Response(
            status_code=status_codes.HTTP_200_OK, headers={}, description="OK"
        )
    prompt = request.json().get("prompt")
    torrents = await find_torrent_list(prompt)
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


@app.options("/v1/file/pin")
@app.post("/v1/file/pin")
async def file_pin(request: Request, _: FileRequest):
    if request.method == "OPTIONS":
        return Response(
            status_code=status_codes.HTTP_200_OK, headers={}, description="OK"
        )
    filename = request.json().get("filename")
    file_path = path.join(DOWNLOAD_DIR, filename)
    if not path.exists(file_path):
        return JSONResponse(
            status_code=status_codes.HTTP_400_BAD_REQUEST,
            headers={},
            description="File not found",
        )
    files = await add_to_ipfs(file_path)
    if files:
        return JSONResponse(
            status_code=status_codes.HTTP_200_OK,
            headers={},
            description={"files": files},
        )
    return JSONResponse(
        status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR,
        headers={},
        description="Error",
    )


@app.options("/v1/file/rm")
@app.post("/v1/file/rm")
async def file_rm(request: Request, _: FileRequest):
    if request.method == "OPTIONS":
        return Response(
            status_code=status_codes.HTTP_200_OK, headers={}, description="OK"
        )
    filename = request.json().get("filename")
    file_path = Path(path.join(DOWNLOAD_DIR, filename))
    if file_path.exists():
        if file_path.is_dir():
            rmtree(file_path.as_posix())
        else:
            file_path.unlink()
    return JSONResponse(
        status_code=status_codes.HTTP_200_OK,
        headers={},
        description="OK",
    )


@app.get("/v1/file/list")
async def file_list():
    try:
        return JSONResponse({"files": listdir(DOWNLOAD_DIR)})
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return Response(
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR,
            headers={},
            description=f"Error listing files: {str(e)}",
        )


if __name__ == "__main__":
    app.start(host="0.0.0.0", port=1789)
