from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    status: str = "success"
    tools_used: list[dict] | None = None
