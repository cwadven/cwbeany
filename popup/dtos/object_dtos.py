from typing import Optional

from pydantic import (
    BaseModel,
    Field,
)

from popup.models import Popup


class PopupModalItem(BaseModel):
    id: int = Field(...)
    title: Optional[str] = Field(...)
    description: Optional[str] = Field(...)
    image_url: Optional[str] = Field(...)
    on_click_link: str = Field(...)
    width: int = Field(...)
    height: int = Field(...)
    top: Optional[int] = Field(...)
    left: Optional[int] = Field(...)

    @classmethod
    def of(cls, popup: Popup, top=None, left=None):
        return cls(
            id=popup.id,
            title=popup.title,
            description=popup.description,
            image_url=popup.image.url if popup.image else None,
            on_click_link=popup.on_click_link,
            width=popup.width,
            height=popup.height,
            top=top,
            left=left,
        )
