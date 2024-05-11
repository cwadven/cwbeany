from typing import (
    Dict,
    List,
)
from django.db.models import (
    Count,
    Q,
    QuerySet,
)
from board.models import (
    Board,
    Post,
    Tag, Reply,
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


def get_tags_active_post_count(tag_ids: List[int]) -> Dict[int, int]:
    if not tag_ids:
        return {}

    return dict(
        Tag.objects.filter(
            id__in=tag_ids,
        ).annotate(
            post_count=Count('post', filter=Q(post__is_active=True)),
        ).values_list(
            'id',
            'post_count',
        )
    )


def update_post_reply_count(post_id: int) -> None:
    post = Post.objects.get(id=post_id)
    post.reply_count = Reply.objects.filter(post_id=post_id).count()
    post.save(update_fields=('reply_count',))
