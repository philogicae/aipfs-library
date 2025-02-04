from logging import getLogger
from pathlib import Path

import coloredlogs
from dotenv import load_dotenv

load_dotenv()
coloredlogs.install()
logger = getLogger("app")

from robyn import ALLOW_CORS, Request, Response, Robyn, status_codes

app = Robyn(__file__)
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
async def completion(request: Request):
    if request.method == "OPTIONS":
        return Response(
            status_code=status_codes.HTTP_200_OK, headers={}, description="OK"
        )
    return Response(
        status_code=status_codes.HTTP_200_OK,
        headers={},
        description=dict(received=request.json().get("prompt")),
    )


if __name__ == "__main__":
    app.start(host="0.0.0.0", port=1789)
