import requests
from collections import defaultdict
from typing import (
    DefaultDict,
    Dict,
    List,
    Optional,
    Set,
    Union,
)

from django.conf import settings
from django.db.models import (
    Count,
    Q,
    QuerySet,
)
from board.models import (
    Board,
    Like,
    Post,
    Reply,
    Rereply,
    Tag,
    UrlImportant,
)
from board.searchs import search_posts
from common.common_utils.paginator_utils import elasticsearch_paging


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


def get_active_filtered_posts(search: str = None,
                              board_urls: List[str] = None,
                              tag_names: List[str] = None) -> QuerySet[Post]:
    q = Q()
    qs = get_active_posts()
    if search:
        q = q & Q(title__icontains=search) | Q(body__icontains=search)
    if board_urls:
        q = q & Q(board__url__in=board_urls)
    if tag_names:
        tag_id_list = Tag.objects.filter(
            tag_name__in=tag_names
        ).values_list(
            'id',
            flat=True
        )
        q = q & Q(tag_set__in=tag_id_list)
        qs = qs.prefetch_related('tag_set')
    return qs.select_related(
        'board',
    ).filter(
        q
    )


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


def get_board_paged_elastic_posts(
        search: str = None,
        page: Union[int, str] = 1,
        board_urls: List[str] = None,
        tag_ids: List[int] = None,
):
    paging_data = elasticsearch_paging(
        search_posts(
            query=search,
            board_urls=board_urls,
            tag_ids=tag_ids,
            sort_fields=['-created_at'],
        ),
        int(page),
        10,
        5,
    )
    return paging_data


def update_post_reply_count(post_id: int) -> None:
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return
    post.reply_count = Reply.objects.filter(post_id=post_id).count()
    post.save(update_fields=('reply_count',))


def update_post_rereply_count(post_id: int) -> None:
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return
    post.rereply_count = Rereply.objects.filter(post_id=post_id).count()
    post.save(update_fields=('rereply_count',))


def update_post_like_count(post_id: int) -> None:
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return
    post.like_count = Like.objects.filter(post_id=post_id).count()
    post.save(update_fields=('like_count',))


def request_n8n_webhook(board_url, post_id) -> None:
    try:
        requests.post(
            url=f'{settings.WEB_HOOK_ADDRESS}',
            data={
                'board_name': board_url,
                'board_id': post_id,
            },
            timeout=5,
        )
    except requests.RequestException:
        pass


def get_liked_post_ids_by_author_id(author_id: Optional[int], post_ids: List[int]) -> Set[int]:
    if not author_id:
        return set()

    if not post_ids:
        return set()

    return set(
        Like.objects.filter(
            author_id=author_id,
            post_id__in=post_ids,
        ).values_list(
            'post_id',
            flat=True,
        )
    )


def get_url_importants(post_id: int) -> List[UrlImportant]:
    return list(
        UrlImportant.objects.filter(
            post_id=post_id,
        )
    )


def get_tags_by_post_id(post_id: int) -> List[Tag]:
    qs = Post.tag_set.through.objects.select_related(
        'tag',
    ).filter(
        post_id=post_id,
    )
    return list(
        q.tag
        for q in qs
    )


def get_replys_by_post_id(post_id: int) -> QuerySet[Reply]:
    return Reply.objects.filter(
        post_id=post_id,
    )


def get_rereplys_by_post_id(post_id: int) -> QuerySet[Rereply]:
    return Rereply.objects.filter(
        post_id=post_id,
    )


def get_value_rereplies_key_rereply_reply_ids_by_post_id(post_id: int) -> DefaultDict[int, List[Rereply]]:
    rereply_by_reply_ids = defaultdict(list)

    for rereply in get_rereplys_by_post_id(post_id).select_related('author__provider'):
        rereply_by_reply_ids[rereply.reply_id].append(rereply)

    return rereply_by_reply_ids
