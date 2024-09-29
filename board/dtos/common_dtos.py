from pydantic import (
    BaseModel,
    Field,
)
from typing import Optional, List


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
