from pydantic import (
    BaseModel,
    Field,
)


class BoardSetGroupResponse(BaseModel):
    board_set: list = Field(...)


class BoardSetBoardInfo(BaseModel):
    name: str = Field(...)
    url: str = Field(...)
