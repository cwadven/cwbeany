from typing import List

from django.db.models import QuerySet
from pydantic import (
    BaseModel,
    Field,
)

from board.dtos.common_dtos import TagInfo


class BoardSetGroupResponse(BaseModel):
    board_set: list = Field(...)


class BoardSetBoardInfo(BaseModel):
    name: str = Field(...)
    url: str = Field(...)


class HomeResponse(BaseModel):
    recent_post_set: Field(...)
    liked_ordered_post_set: Field(...)
    tag_infos: List[TagInfo] = Field(
        default_factory=list,
        description='태그 이름과 각 태그의 게시물 수 목록',
    )
    announce_set: Field(...)
    lesson: Field(...)
