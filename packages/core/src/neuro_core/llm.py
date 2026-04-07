from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatExecutionRequest(BaseModel):
    provider: str
    model: str
    messages: list[ChatMessage]
    max_output_tokens: int | None = None


class ChatExecutionResponse(BaseModel):
    provider: str
    model: str
    output_text: str
    finish_reason: str | None = None
    transport: str
    raw_response: dict | None = None

