import json
from constance import config
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.templatetags.static import static

from board.consts import BOARD_HOME_PATH
from board.dtos.common_dtos import (
    BoardPost,
    DetailPost,
    DetailPostNavigation,
    DetailPostReply,
    DetailPostRereply,
    DetailPostSummary,
    DetailPostTag,
    HomePost,
    ImportantUrl,
    RecentBoardPostLayer,
    RecentPost,
    TagInfo,
)
from board.dtos.request_dtos import (
    BoardPostsRequest,
    TaggedPostsRequest,
)
from board.dtos.response_dtos import (
    HomeResponse,
    BoardSetBoardInfo,
    BoardSetGroupResponse,
    BoardPostsResponse,
    BoardDetailInfo, PostDetailResponse,
)
from board.models import (
    Board,
    Like,
    Post,
    Reply,
    Rereply,
    Tag,
)
from board.services import (
    get_active_filtered_posts,
    get_active_posts,
    get_board_paged_elastic_posts,
    get_boards_by_board_group_id,
    get_liked_post_ids_by_author_id,
    get_tags,
    get_tags_active_post_count,
    get_tags_by_post_id,
    get_url_importants,
    update_post_like_count,
    update_post_reply_count,
    update_post_rereply_count,
    get_replys_by_post_id,
    get_value_rereplies_key_rereply_reply_ids_by_post_id,
)
from chatgpt.dtos.common_dtos import HomeLesson
from chatgpt.services import (
    get_latest_post_summary_by_post_id,
    get_lessons,
)
from common.common_utils.redis_utils import RedisQueue
from common.common_utils.string_utils import replace_special_char
from config import settings
from control.dtos.common_dtos import AnnounceInfo
from control.services import get_announces


def get_boards_info_from_board_group(request, board_group_id: int):
    return HttpResponse(
        BoardSetGroupResponse(
            board_set=[
                BoardSetBoardInfo(
                    name=_board.name,
                    url=_board.url
                ) for _board in get_boards_by_board_group_id(board_group_id)
            ]
        ).model_dump_json(),
        'application/json',
    )


def home(request):
    recent_post_qs = get_active_posts().select_related(
        'board',
    ).order_by(
        '-id'
    ).only(
        'id',
        'board__url',
        'title',
        'body',
        'post_img',
        'created_at',
    )[:6]
    liked_ordered_post_qs = get_active_posts().select_related(
        'board',
        'author',
    ).order_by(
        '-like_count',
        '-reply_count',
        '-id',
    ).only(
        'id',
        'board__url',
        'author__nickname',
        'title',
        'body',
        'created_at',
        'like_count',
        'reply_count',
        'rereply_count',
    )[:6]
    tags = get_tags()
    post_count_by_tag_id = get_tags_active_post_count([tag.id for tag in tags])
    lesson = get_lessons().last()
    return render(
        request,
        BOARD_HOME_PATH,
        HomeResponse(
            recent_posts=[
                HomePost(
                    id=recent_post.id,
                    board_url=recent_post.board.url,
                    title=recent_post.title,
                    short_body=recent_post.short_body(),
                    image_url=recent_post.post_img.url if recent_post.post_img else static('logo.ico'),
                    created_at=recent_post.created_at.strftime('%Y-%m-%d'),
                )
                for recent_post in recent_post_qs
            ],
            liked_ordered_posts=[
                HomePost(
                    id=liked_ordered_post.id,
                    board_url=liked_ordered_post.board.url,
                    title=liked_ordered_post.title,
                    body=liked_ordered_post.body,
                    like_count=liked_ordered_post.like_count,
                    reply_count=liked_ordered_post.reply_count + liked_ordered_post.rereply_count,
                    author_nickname=liked_ordered_post.author.nickname,
                    created_at=liked_ordered_post.created_at.strftime('%Y-%m-%d'),
                )
                for liked_ordered_post in liked_ordered_post_qs
            ],
            tag_infos=[
                TagInfo(
                    tag_name=_tag.tag_name,
                    post_count=post_count_by_tag_id.get(_tag.id, 0),
                ) for _tag in tags
            ],
            announce_infos=[
                AnnounceInfo(
                    title=announce.title,
                    body=announce.body,
                    created_at=announce.created_at.strftime('%Y-%m-%d'),
                ) for announce in get_announces().order_by('-id')[:5]
            ],
            lesson=HomeLesson(
                summary=lesson.summary,
                body=replace_special_char(lesson.body),
            ) if lesson else None,
            profile_description=mark_safe(config.PROFILE_DESCRIPTION_MARKDOWN),
            profile_image_url=settings.MEDIA_URL + config.PROFILE_IMAGE_URL,
            profile_name=config.PROFILE_NAME,
            profile_simple_description=config.PROFILE_SIMPLE_DESCRIPTION,
        ).model_dump(),
    )


def get_all_board_posts(request):
    board_posts_request = BoardPostsRequest.of(request)
    board_detail_display = '전체 게시판'
    if board_posts_request.search:
        board_detail_display = board_posts_request.search

    paging_data = get_board_paged_elastic_posts(
        search=board_posts_request.search,
        page=request.GET.get('page', 1)
    )
    page_posts = paging_data['page_posts']
    has_previous = paging_data['has_previous']
    has_next = paging_data['has_next']
    return render(
        request,
        'board/all_board_detail.html',
        BoardPostsResponse(
            board_detail_info=BoardDetailInfo(
                name=board_detail_display,
                info=board_detail_display,
                url=board_detail_display,
            ),
            posts=[
                BoardPost(
                    id=post.id,
                    title=post.title,
                    short_body=replace_special_char(" ".join(post.body.split()[:50])),
                    board_url=post.board.url,
                    author_nickname=post.author.nickname,
                    created_at=post.created_at.strftime('%Y-%m-%d'),
                    like_count=post.like_count,
                    reply_count=post.reply_count + post.rereply_count,
                    image_url=post.post_img if post.post_img else static('logo.ico'),
                ) for post in page_posts
            ],
            has_previous=has_previous,
            has_next=has_next,
            previous_page_number=paging_data['previous_page_number'] if has_previous else None,
            current_page_number=paging_data['current_page'],
            next_page_number=paging_data['next_page_number'] if has_next else None,
            last_page_number=paging_data['num_pages'],
            page_range=paging_data['page_range'],
        ).model_dump()
    )


def get_board_posts(request, board_url):
    board_detail = get_object_or_404(Board, url=board_url)

    board_posts_request = BoardPostsRequest.of(request)

    paging_data = get_board_paged_elastic_posts(
        search=board_posts_request.search,
        board_urls=[board_url],
        page=request.GET.get('page', 1)
    )
    page_posts = paging_data['page_posts']
    has_previous = paging_data['has_previous']
    has_next = paging_data['has_next']
    return render(
        request,
        'board/board_detail.html',
        BoardPostsResponse(
            board_detail_info=BoardDetailInfo(
                name=board_detail.name,
                info=board_detail.info,
                url=board_detail.url,
                board_img_url=board_detail.board_img.url if board_detail.board_img else None,
                name_background_color=board_detail.name_background_color,
                name_text_color=board_detail.name_text_color,
                info_background_color=board_detail.info_background_color,
                info_text_color=board_detail.info_text_color,
            ),
            posts=[
                BoardPost(
                    id=post.id,
                    title=post.title,
                    short_body=replace_special_char(" ".join(post.body.split()[:50])),
                    board_url=post.board.url,
                    author_nickname=post.author.nickname,
                    created_at=post.created_at.strftime('%Y-%m-%d'),
                    like_count=post.like_count,
                    reply_count=post.reply_count + post.rereply_count,
                    image_url=post.post_img if post.post_img else static('logo.ico'),
                ) for post in page_posts
            ],
            has_previous=has_previous,
            has_next=has_next,
            previous_page_number=paging_data['previous_page_number'] if has_previous else None,
            current_page_number=paging_data['current_page'],
            next_page_number=paging_data['next_page_number'] if has_next else None,
            last_page_number=paging_data['num_pages'],
            page_range=paging_data['page_range'],
        ).model_dump()
    )


def get_tagged_posts(request, tag_name):
    tagged_posts_request = TaggedPostsRequest.of(request)
    tag = get_object_or_404(Tag, tag_name=tag_name)

    paging_data = get_board_paged_elastic_posts(
        search=tagged_posts_request.search,
        tag_ids=[tag.id],
        page=request.GET.get('page', 1)
    )
    page_posts = paging_data['page_posts']
    has_previous = paging_data['has_previous']
    has_next = paging_data['has_next']
    return render(
        request,
        'board/tagged_board_detail.html',
        BoardPostsResponse(
            board_detail_info=BoardDetailInfo(
                name=tag_name,
                info=tag_name,
                url=tag_name,
            ),
            posts=[
                BoardPost(
                    id=post.id,
                    title=post.title,
                    short_body=replace_special_char(" ".join(post.body.split()[:50])),
                    board_url=post.board.url,
                    author_nickname=post.author.nickname,
                    created_at=post.created_at.strftime('%Y-%m-%d'),
                    like_count=post.like_count,
                    reply_count=post.reply_count + post.rereply_count,
                    image_url=post.post_img if post.post_img else static('logo.ico'),
                ) for post in page_posts
            ],
            has_previous=has_previous,
            has_next=has_next,
            previous_page_number=paging_data['previous_page_number'] if has_previous else None,
            current_page_number=paging_data['current_page'],
            next_page_number=paging_data['next_page_number'] if has_next else None,
            last_page_number=paging_data['num_pages'],
            page_range=paging_data['page_range'],
        ).model_dump()
    )


# 자세한 글 보기
def post_detail(request, board_url: str, pk: int):
    active_filtered_posts = get_active_filtered_posts(board_urls=[board_url])

    prev_post = active_filtered_posts.filter(id__lt=pk).last()
    next_post = active_filtered_posts.filter(id__gt=pk).order_by('id').first()

    post = get_object_or_404(active_filtered_posts.select_related('author'), pk=pk)
    post_summary = get_latest_post_summary_by_post_id(post.id)

    replies = get_replys_by_post_id(post.id).select_related('author__provider')
    rereplies_by_reply_ids = get_value_rereplies_key_rereply_reply_ids_by_post_id(post.id)

    return render(
        request,
        'board/post.html',
        PostDetailResponse(
            is_liked=bool(get_liked_post_ids_by_author_id(request.user.id, [post.id])),
            recent_board_post_layer=RecentBoardPostLayer(
                board_url=board_url,
                board_name=post.board.name,
                posts=[
                    RecentPost(
                        id=recent_post.id,
                        title=recent_post.title,
                        reply_count=recent_post.reply_count + recent_post.rereply_count,
                    )
                    for recent_post in active_filtered_posts.order_by('-id')[:5]
                ],
            ),
            post=DetailPost(
                id=post.id,
                board_url=post.board.url,
                board_name=post.board.name,
                board_info=post.board.info,
                author_nickname=post.author.nickname,
                title=post.title,
                simple_body=post.short_body(),
                body=mark_safe(post.body),
                main_image_url=(
                    post.post_img.url if post.post_img else None
                ),
                like_count=post.like_count,
                reply_count=post.reply_count + post.rereply_count,
                created_at=post.created_at.strftime('%Y-%m-%d'),
            ),
            post_summary=DetailPostSummary(
                status=post_summary.status,
                body=post_summary.body,
            ) if post_summary else None,
            prev_post_navigation=DetailPostNavigation(
                post_id=prev_post.id,
                board_url=prev_post.board.url,
            ) if prev_post else None,
            next_post_navigation=DetailPostNavigation(
                post_id=next_post.id,
                board_url=next_post.board.url,
            ) if next_post else None,
            important_urls=[
                ImportantUrl(url=url_important.url)
                for url_important in get_url_importants(post.id)
            ],
            tags=[
                DetailPostTag(name=tag.tag_name)
                for tag in get_tags_by_post_id(post.id)
            ],
            replies=[
                DetailPostReply(
                    id=reply.id,
                    body=reply.body,
                    author_id=reply.author_id,
                    author_image_url=(
                        reply.author.user_img.url
                        if reply.author.user_img else None
                    ),
                    author_nickname=reply.author.nickname,
                    author_provider_name=reply.author.provider and reply.author.provider.provider_name,
                    created_at=reply.created_at.strftime('%Y-%m-%d'),
                    rereplies=[
                        DetailPostRereply(
                            id=rereply.id,
                            body=rereply.body,
                            author_id=rereply.author_id,
                            author_image_url=(
                                rereply.author.user_img.url
                                if rereply.author.user_img else None
                            ),
                            author_nickname=rereply.author.nickname,
                            author_provider_name=rereply.author.provider and rereply.author.provider.provider_name,
                            created_at=rereply.created_at.strftime('%Y-%m-%d'),
                        )
                        for rereply in rereplies_by_reply_ids[reply.id]
                    ]
                ) for reply in replies
            ],
        ).model_dump(),
    )


# 댓글 작성
@login_required(login_url='/')
def reply_write(request, board_url, pk):
    if request.method == 'POST':
        post = get_object_or_404(Post, board__url=board_url, pk=pk)
        if request.POST.get('reply_body'):
            Reply.objects.create(post=post, author=request.user, body=request.POST.get('reply_body'))
            update_post_reply_count(pk)

    return HttpResponseRedirect(reverse('board:post', args=[board_url, pk]))


# 답글 작성
@login_required(login_url='/')
def rereply_write(request, board_url, pk):
    reply = get_object_or_404(Reply, id=pk)
    if request.method == 'POST' and request.POST.get('rereply'):
        rereply = Rereply()
        rereply.post = reply.post
        rereply.reply = reply
        rereply.author = request.user
        rereply.body = request.POST.get('rereply')
        rereply.save()
        update_post_rereply_count(reply.post_id)
    return HttpResponseRedirect(reverse('board:post', args=[board_url, reply.post.id]))


# 댓글 삭제
@login_required(login_url='/')
def reply_delete(request, board_url, pk):
    reply = get_object_or_404(Reply, id=pk)
    post_id = reply.post.id
    if reply.author == request.user or request.user.is_superuser:
        reply.delete()
        update_post_reply_count(post_id)
        update_post_rereply_count(post_id)
    return HttpResponseRedirect(reverse('board:post', args=[board_url, post_id]))


# 답글 삭제
@login_required(login_url='/')
def rereply_delete(request, board_url, pk):
    rereply = get_object_or_404(Rereply, id=pk)
    post_id = rereply.post.id
    if rereply.author == request.user or request.user.is_superuser:
        rereply.delete()
        update_post_rereply_count(post_id)
    return HttpResponseRedirect(reverse('board:post', args=[board_url, post_id]))


# 좋아요 추가 삭제
@login_required(login_url='/')
def like(request, board_url, pk):
    post = get_object_or_404(Post, id=pk)
    qs = Like.objects.filter(author=request.user, post=post)
    if qs.exists():
        qs.delete()
    else:
        Like.objects.create(author=request.user, post=post)
    update_post_like_count(pk)
    return HttpResponseRedirect(reverse('board:post', args=[board_url, pk]))


@login_required(login_url='/')
def post_temporary_save(request):
    request_data = json.loads(request.body)
    queue_name = request_data.get('queue_name')
    value = request_data.get('value')

    if not queue_name or not value:
        return JsonResponse({'message': '"queue_name", "value" is required'}, status=400)

    redis_queue = RedisQueue(queue_name, ttl=60 * 30, max_size=5)
    if redis_queue.get_last() != value:
        redis_queue.enqueue(value)
    return JsonResponse({'message': 'success'}, status=200)


@login_required(login_url='/')
def get_temporary_save(request):
    queue_name = request.GET.get('queue_name')
    if not queue_name:
        return JsonResponse({'message': '"queue_name" is required'}, status=400)

    redis_queue = RedisQueue(queue_name)
    return JsonResponse({'data': redis_queue.get_all()}, status=200)
