from pydantic import (
    BaseModel,
    Field,
)


class TagInfo(BaseModel):
    tag_name: str = Field(...)
    post_count: int = Field(...)


class Post(BaseModel):
    id: int = Field(..., description='게시글 ID')
    board_url: str = Field(..., description='게시판 URL')
    title: str = Field(default='', description='제목')
    body: str = Field(default='', description='본문 전체')
    short_body: str = Field(default='', description='본문의 앞부분 100자')
    image_url: str = Field(default='', description='이미지 URL')
    like_count: int = Field(default=0, description='좋아요 수')
    reply_count: int = Field(default=0, description='댓글 수')
    author_nickname: str = Field(default='', description='작성자 닉네임')
    created_at: str = Field(..., description='작성일')


class HomePost(BaseModel):
    pass
