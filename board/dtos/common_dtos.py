from pydantic import (
    BaseModel,
    Field,
)
from typing import (
    Any,
    List,
    Optional,
)


class TagInfo(BaseModel):
    tag_name: str = Field(...)
    post_count: int = Field(...)


class BoardPost(BaseModel):
    id: int = Field(..., description='게시글 ID')
    board_url: str = Field(..., description='게시판 URL')
    title: str = Field(default='', description='제목')
    body: Optional[str] = Field(default='', description='본문 전체')
    short_body: str = Field(default='', description='본문의 앞부분 100자')
    image_url: str = Field(default='', description='이미지 URL')
    like_count: int = Field(default=0, description='좋아요 수')
    reply_count: int = Field(default=0, description='댓글 수')
    author_nickname: str = Field(default='', description='작성자 닉네임')
    created_at: str = Field(..., description='작성일')


class HomePost(BoardPost):
    pass


class RecentPost(BaseModel):
    id: int = Field(..., description='게시글 ID')
    title: str = Field(default='', description='제목')
    reply_count: int = Field(default=0, description='댓글 수')


class RecentBoardPostLayer(BaseModel):
    board_url: str = Field(..., description='게시판 URL')
    board_name: str = Field(..., description='게시판 이름')
    posts: Optional[List[RecentPost]] = Field(
        default_factory=list,
        description='게시판의 최근 게시물 목록',
    )


class ImportantUrl(BaseModel):
    url: str = Field(..., description='URL')


class DetailPostTag(BaseModel):
    name: str = Field(..., description='태그 이름')


class DetailPostRereply(BaseModel):
    id: int = Field(..., description='대댓글 ID')
    body: str = Field(..., description='대댓글 본문')
    author_id: int = Field(..., description='작성자 ID')
    author_image_url: Optional[str] = Field(..., description='작성자 프로필 사진')
    author_nickname: Optional[str] = Field(..., description='작성자 닉네임')
    author_provider_name: Optional[str] = Field(..., description='작성자 소셜 로그인 제공자 이름')
    created_at: str = Field(..., description='작성일')


class DetailPostReply(BaseModel):
    id: int = Field(..., description='댓글 ID')
    body: str = Field(..., description='댓글 본문')
    author_id: int = Field(..., description='작성자 ID')
    author_image_url: Optional[str] = Field(..., description='작성자 프로필 사진')
    author_nickname: Optional[str] = Field(..., description='작성자 닉네임')
    author_provider_name: Optional[str] = Field(..., description='작성자 소셜 로그인 제공자 이름')
    created_at: str = Field(..., description='작성일')
    rereplies: Optional[List[DetailPostRereply]] = Field(
        default_factory=list,
        description='대댓글 목록',
    )


class DetailPost(BaseModel):
    id: int = Field(..., description='게시글 ID')
    board_url: Optional[str] = Field(..., description='게시판 URL')
    board_name: Optional[str] = Field(..., description='게시판 이름')
    board_info: Optional[str] = Field(..., description='게시판 정보')
    author_nickname: Optional[str] = Field(..., description='작성자 닉네임')
    title: str = Field(..., description='제목')
    simple_body: str = Field(..., description='본문의 앞부분 100자')
    body: Any = Field(..., description='본문 전체')
    main_image_url: Optional[str] = Field(..., description='대표 이미지 URL')
    like_count: int = Field(..., description='좋아요 수')
    reply_count: int = Field(..., description='댓글 수')
    created_at: str = Field(..., description='작성일')


class DetailPostSummary(BaseModel):
    status: str = Field(..., description='상태')
    body: Optional[str] = Field(..., description='본문')


class DetailPostNavigation(BaseModel):
    post_id: int = Field(..., description='게시글 ID')
    board_url: Optional[str] = Field(..., description='게시판 URL')
