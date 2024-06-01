from pydantic import (
    BaseModel,
    Field,
)
from typing import Optional


class BoardPostsRequest(BaseModel):
    search: Optional[str] = Field(...)

    @staticmethod
    def of(request):
        return BoardPostsRequest(
            search=request.GET.get('search'),
        )
