from robyn.types import Body, JSONResponse


class UserMessage(Body):
    user_id: str
    chat_id: str
    message: str


class AgentMessage(JSONResponse):
    user_id: str
    chat_id: str
    message: str
