from typing import (
    List,
    Optional,
)

from pydantic import (
    BaseModel,
    Field,
)

from board.dtos.common_dtos import (
    BoardPost,
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


class BoardDetailInfo(BaseModel):
    name: str = Field(...)
    info: str = Field(...)
    url: str = Field(...)
    board_img_url: Optional[str] = Field(...)
    name_background_color: Optional[str] = Field(...)
    name_text_color: Optional[str] = Field(...)
    info_background_color: Optional[str] = Field(...)
    info_text_color: Optional[str] = Field(...)


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


class BoardPostsResponse(BaseModel):
    board_detail_info: BoardDetailInfo = Field(
        ...,
        description='게시판 정보',
    )
    posts: List[BoardPost] = Field(
        default_factory=list,
        description='게시물 목록',
    )
    page_range: Optional[List[int]] = Field(
        default_factory=list,
        description='페이지 범위',
    )
