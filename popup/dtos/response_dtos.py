from pydantic import (
    BaseModel,
    Field,
)


class PopupModalResponse(BaseModel):
    modals: list = Field(...)
