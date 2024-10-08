from typing import (
    Any,
    List,
    Optional,
)

from pydantic import (
    BaseModel,
    Field,
)

from board.dtos.common_dtos import (
    BoardPost,
    DetailPost,
    DetailPostNavigation,
    DetailPostReply,
    DetailPostSummary,
    DetailPostTag,
    HomePost,
    ImportantUrl,
    RecentBoardPostLayer,
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
    board_img_url: Optional[str] = Field(default=None)
    name_background_color: Optional[str] = Field(default=None)
    name_text_color: Optional[str] = Field(default=None)
    info_background_color: Optional[str] = Field(default=None)
    info_text_color: Optional[str] = Field(default=None)


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
    profile_description: Optional[Any] = Field(
        None,
        description='홈 화면에 Profile 정보 MarkDown',
    )
    profile_image_url: Optional[str] = Field(
        None,
        description='홈 화면에 Profile 사진 URL',
    )
    profile_name: Optional[str] = Field(
        None,
        description='홈 화면에 Profile 이름',
    )
    profile_simple_description: Optional[str] = Field(
        None,
        description='홈 화면에 Profile 간단 소개',
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
    has_previous: bool = Field(
        ...,
        description='이전 페이지 존재 여부',
    )
    has_next: bool = Field(
        ...,
        description='다음 페이지 존재 여부',
    )
    previous_page_number: Optional[int] = Field(
        ...,
        description='이전 페이지 번호',
    )
    current_page_number: int = Field(
        ...,
        description='현재 페이지 번호',
    )
    next_page_number: Optional[int] = Field(
        ...,
        description='다음 페이지 번호',
    )
    last_page_number: int = Field(
        ...,
        description='마지막 페이지 번호',
    )
    page_range: Optional[List[int]] = Field(
        default_factory=list,
        description='페이지 범위',
    )


class PostDetailResponse(BaseModel):
    is_liked: bool = Field(..., description='좋아요 여부')
    recent_board_post_layer: RecentBoardPostLayer = Field(..., description='최근 게시물 목록')
    post: DetailPost = Field(..., description='게시글 정보')
    post_summary: Optional[DetailPostSummary] = Field(..., description='게시글 요약 정보')
    prev_post_navigation: Optional[DetailPostNavigation] = Field(..., description='이전 게시글 정보')
    next_post_navigation: Optional[DetailPostNavigation] = Field(..., description='다음 게시글 정보')
    important_urls: List[ImportantUrl] = Field(default_factory=list, description='중요 URL 목록')
    tags: List[DetailPostTag] = Field(default_factory=list, description='태그 목록 정보')
    replies: List[DetailPostReply] = Field(default_factory=list, description='댓글 목록')
