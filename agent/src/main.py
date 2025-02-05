from logging import getLogger
from pathlib import Path

import coloredlogs
from dotenv import load_dotenv

load_dotenv()
coloredlogs.install()
logger = getLogger("agent")

from robyn import ALLOW_CORS, Request, Response, Robyn, status_codes
from robyn.openapi import Components, OpenAPI, OpenAPIInfo
from robyn.types import Body, JSONResponse
from scraper_test import find_torrents


class Completion(Body):
    prompt: str


class CompletionResponse(JSONResponse):
    result: dict


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


@app.get("/")
async def index():
    return Response(
        status_code=status_codes.HTTP_200_OK, headers={}, description="Hello world!"
    )


@app.options("/api/completion")
@app.post("/api/completion")
async def completion(request: Request, _: Completion):
    if request.method == "OPTIONS":
        return Response(
            status_code=status_codes.HTTP_200_OK, headers={}, description="OK"
        )
    prompt = request.json().get("prompt")
    torrents = await find_torrents(prompt)
    return CompletionResponse(result=torrents)


if __name__ == "__main__":
    app.start(host="0.0.0.0", port=1789)
