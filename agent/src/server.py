from logging import getLogger

import coloredlogs
from dotenv import load_dotenv

load_dotenv()
coloredlogs.install()
logger = getLogger("server")

from robyn import ALLOW_CORS, Request, Response, Robyn
from robyn.openapi import Components, OpenAPI, OpenAPIInfo
from robyn.status_codes import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from agentkit import Agent
from models import UserMessage

agent = Agent()

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


async def startup():
    logger.info("Starting up...")
    await agent.init()
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


@app.options("/v1/chat")
@app.post("/v1/chat")
async def chat(request: Request, _: UserMessage):
    try:
        if request.method == "OPTIONS":
            return Response(status_code=HTTP_200_OK, headers={}, description="OK")
        return await agent.chat(request.json())
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return Response(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            headers={},
            description=f"Error in chat: {str(e)}",
        )


@app.options("/v1/chat/stream")
@app.post("/v1/chat/stream")
async def chat_stream(request: Request, _: UserMessage):
    try:
        if request.method == "OPTIONS":
            return Response(status_code=HTTP_200_OK, headers={}, description="OK")
        # TODO
        return await agent.chat_stream(request.json())
    except Exception as e:
        logger.error(f"Error in chat stream: {str(e)}")
        return Response(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            headers={},
            description=f"Error in chat stream: {str(e)}",
        )


if __name__ == "__main__":
    app.start(host="0.0.0.0", port=1789)
