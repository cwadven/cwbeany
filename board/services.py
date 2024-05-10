from typing import List

from django.db.models import QuerySet

from board.models import (
    Board,
    Post,
    Tag,
)


def get_boards_by_board_group_id(board_group_id: int) -> List[Board]:
    return list(
        Board.objects.filter(
            board_group_id=board_group_id,
        )
    )


def get_active_posts() -> QuerySet[Post]:
    return Post.objects.active()


def get_tags() -> QuerySet[Tag]:
    return Tag.objects.all()
