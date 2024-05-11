from pydantic import (
    BaseModel,
    Field,
)


class AnnounceInfo(BaseModel):
    title: str = Field(...)
    body: str = Field(...)
    created_at: str = Field(...)
