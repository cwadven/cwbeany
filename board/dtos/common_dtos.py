from pydantic import (
    BaseModel,
    Field,
)


class TagInfo(BaseModel):
    tag_name: str = Field(...)
    post_count: int = Field(...)
