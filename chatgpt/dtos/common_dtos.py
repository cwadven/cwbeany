from pydantic import (
    BaseModel,
    Field,
)


class HomeLesson(BaseModel):
    summary: str = Field(...)
    body: str = Field(...)


class ChatGPTConversationEntry(BaseModel):
    role: str = Field(...)
    content: str = Field(...)
