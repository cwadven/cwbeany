from typing import List, Optional

from pydantic import (
    BaseModel,
    Field,
)

from board.dtos.common_dtos import (
    HomePost,
    TagInfo,
)
from chatgpt.dtos.common_dtos import HomeLesson
from control.dtos.common_dtos import AnnounceInfo


class BoardSetGroupResponse(BaseModel):
    board_set: list = Field(...)


class BoardSetBoardInfo(BaseModel):
    name: str = Field(...)
    url: str = Field(...)


class HomeResponse(BaseModel):
    recent_posts: List[HomePost] = Field(
        default_factory=list,
        description='최근 게시물 목록',
    )
    liked_ordered_posts: List[HomePost] = Field(
        default_factory=list,
        description='좋아요 게시물 목록',
    )
    tag_infos: List[TagInfo] = Field(
        default_factory=list,
        description='태그 이름과 각 태그의 게시물 수 목록',
    )
    announce_infos: List[AnnounceInfo] = Field(
        default_factory=list,
        description='공지사항 목록',
    )
    lesson: Optional[HomeLesson] = Field(
        None,
        description='홈 화면에 표시할 ChatGPT 학습 정보',
    )
