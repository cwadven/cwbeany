from django.urls import path
from .views import *

app_name = 'board'

urlpatterns = [
    path('', home, name='home'),
    path('board', get_all_board_posts, name='all_board_posts'),
    path('board/tag/<str:tag_name>', get_tagged_posts, name='get_tagged_posts'),
    path('board/<str:board_url>', get_board_posts, name='get_board_posts'),
    path('<str:board_url>/<int:pk>', post_detail, name='post'),
    path('<str:board_url>/<int:pk>/reply', reply_write, name='reply'),
    path('<str:board_url>/<int:pk>/rereply', rereply_write, name='rereply'),
    path('<str:board_url>/<int:pk>/reply_del', reply_delete, name='reply_delete'),
    path('<str:board_url>/<int:pk>/rereply_del', rereply_delete, name='rereply_delete'),
    path('<str:board_url>/<int:pk>/like', like, name='like'),
    path('board-group/<int:board_group_id>/constant', get_boards_info_from_board_group, name='get_boards_info_from_board_group'),

    path('post/temporary-save', post_temporary_save, name='post_temporary_save'),
    path('post/get-temporary-save', get_temporary_save, name='get_temporary_save'),
]
