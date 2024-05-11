from django.contrib.auth.decorators import login_required
from django.db.models import (
    Count,
    Q,
)
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
)
from django.urls import reverse
from django.templatetags.static import static

from board.consts import BOARD_HOME_PATH
from board.dtos.common_dtos import (
    HomePost,
    TagInfo,
)
from board.dtos.response_dtos import (
    HomeResponse,
    BoardSetBoardInfo,
    BoardSetGroupResponse,
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
    get_active_posts,
    get_boards_by_board_group_id,
    get_tags, get_tags_active_post_count,
)
from chatgpt.dtos.common_dtos import HomeLesson
from chatgpt.services import get_lessons
from common.common_utils.paginator_utils import web_paging
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
    ).annotate(
        reply_count=Count('replys', distinct=True) + Count('rereply', distinct=True),
        like_count=Count('likes', distinct=True),
    ).order_by(
        '-like_count',
        '-reply_count',
        '-id',
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
                    reply_count=liked_ordered_post.reply_count,
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
                body=lesson.body,
            ) if lesson else None,
        ).model_dump(),
    )


# 게시글 목록 (게시판)
def board(request, board_url):
    q = Q()

    board_obj = None
    tag_board = None

    # page:
    # 1 게시판 페이지
    # 2 태그 페이지
    # 3 검색 페이지
    page = 1

    search = request.GET.get('search')

    # 태그 페이지
    if board_url[0] == '_':
        page = 2
        tag_option = board_url[1:]

    # 검색 페이지
    if board_url == 'search':
        page = 3

    if search:
        tag_id_list = Tag.objects.filter(
            tag_name__icontains=search
        ).values_list(
            'id', flat=True
        )

        q = q & Q(title__icontains=search) | Q(body__icontains=search) | Q(tag_set__in=tag_id_list)

    # 게시판 선택
    if page == 1:
        board_obj = get_object_or_404(Board, url=board_url)
        posts = board_obj.post_set.filter(q).annotate(
            reply_count=Count('replys', distinct=True) + Count('rereply', distinct=True),
            like_count=Count('likes', distinct=True),
        ).order_by(
            '-created_at'
        )
    # 태그 검색
    elif page == 2:
        tag_board = get_object_or_404(Tag, tag_name=tag_option)
        posts = tag_board.post_set.filter(q).annotate(
            reply_count=Count('replys', distinct=True) + Count('rereply', distinct=True),
            like_count=Count('likes', distinct=True),
        ).order_by(
            '-created_at'
        )
    # 전체 검색
    elif page == 3:
        posts = Post.objects.active().filter(q).annotate(
            reply_count=Count('replys', distinct=True) + Count('rereply', distinct=True),
            like_count=Count('likes', distinct=True),
        ).order_by(
            '-created_at'
        )

    paging_obj = web_paging(
        posts,
        int(request.GET.get('page', 1)),
        10,
        5,
    )

    context = {
        'posts': paging_obj.get('page_posts'),
        'page_range': paging_obj.get('page_range'),
        'board': board_obj,
        'tag_board': tag_board,
    }

    return render(request, 'board/board.html', context)


# 자세한 글 보기
def post_detail(request, board_url, pk):
    qs = Post.objects.active().filter(
        board__url=board_url
    ).select_related(
        'board'
    ).order_by(
        '-id'
    )

    prev_post = qs.filter(id__lt=pk).first()
    next_post = qs.filter(id__gt=pk).order_by('id').first()

    qs = qs.annotate(
        reply_count=Count('replys', distinct=True) + Count('rereply', distinct=True),
        like_count=Count('likes', distinct=True),
    )

    post = get_object_or_404(qs, board__url=board_url, pk=pk)

    if request.user.is_authenticated:
        like_check = Like.objects.filter(author=request.user, post=post).exists()
    else:
        like_check = False

    context = {
        'like_check': like_check,
        'qs': qs,
        'post': post,
        'prev_post': prev_post,
        'next_post': next_post,
    }

    return render(request, 'board/post.html', context)


# 댓글 작성
@login_required(login_url='/')
def reply_write(request, board_url, pk):
    if request.method == 'POST':
        post = get_object_or_404(Post, board__url=board_url, pk=pk)
        if request.POST.get('reply_body'):
            Reply.objects.create(post=post, author=request.user, body=request.POST.get('reply_body'))

    return HttpResponseRedirect(reverse('board:post', args=[board_url, pk]))


# 답글 작성
@login_required(login_url='/')
def rereply_write(request, board_url, pk):
    reply = get_object_or_404(Reply, id=pk)
    if request.method == 'POST' and request.POST.get('rereply'):
        rereply = Rereply()
        rereply.reply = reply
        rereply.author = request.user
        rereply.body = request.POST.get('rereply')
        rereply.save()
    return HttpResponseRedirect(reverse('board:post', args=[board_url, reply.post.id]))


# 댓글 삭제
@login_required(login_url='/')
def reply_delete(request, board_url, pk):
    reply = get_object_or_404(Reply, id=pk)
    post_id = reply.post.id
    if reply.author == request.user or request.user.is_superuser:
        reply.delete()
    return HttpResponseRedirect(reverse('board:post', args=[board_url, post_id]))


# 답글 삭제
@login_required(login_url='/')
def rereply_delete(request, board_url, pk):
    rereply = get_object_or_404(Rereply, id=pk)
    post_id = rereply.post.id
    if rereply.author == request.user or request.user.is_superuser:
        rereply.delete()
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
    return HttpResponseRedirect(reverse('board:post', args=[board_url, pk]))
