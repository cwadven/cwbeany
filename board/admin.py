import requests

from django.contrib import admin
from .models import *


class RereplyInline(admin.TabularInline):
    model = Rereply


class ReplyInline(admin.TabularInline):
    model = Reply


class LikeInline(admin.TabularInline):
    model = Like


class UrlImportantInline(admin.TabularInline):
    model = UrlImportant


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'url',
        'name',
        'info',
        'info_text_color',
        'attribute',
        'board_group_name',
    )

    def board_group_name(self, obj):
        if obj.board_group:
            return obj.board_group.group_name
        return None


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [
        UrlImportantInline,
        ReplyInline,
        RereplyInline,
        LikeInline,
    ]
    list_filter = (
        'board__name',
    )
    search_fields = (
        'title',
        'body',
        'author__username',
        'author__nickname',
        'author__email',
    )
    list_display = (
        'id',
        'author',
        'board_name',
        'title',
        '_tag_set',
        '_comment_count',
        '_like_count',
    )

    def get_queryset(self, request):
        qs = super(PostAdmin, self).get_queryset(request)
        qs = qs.annotate(
            _comment_count=models.Count('replys', distinct=True) + models.Count('rereply', distinct=True),
            _like_count=models.Count('likes', distinct=True),
        )
        return qs

    def board_name(self, obj):
        if obj.board:
            return obj.board.name
        return None

    def author(self, obj):
        if obj.author:
            return obj.author.nickname
        return None

    def _tag_set(self, obj):
        if obj.tag_set.exists():
            return ", ".join([tag.tag_name for tag in obj.tag_set.all()])
        return None

    def _comment_count(self, obj):
        return obj._comment_count

    def _like_count(self, obj):
        return obj._like_count

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        instance = form.instance
        if instance.def_tag:
            instance.tag_save()

        try:
            if instance.is_active:
                requests.post(
                    url=f'{settings.WEB_HOOK_ADDRESS}/webhook/0e70fe59-69db-4641-88f9-aa50888f3561',
                    data={
                        'board_name': instance.board.url,
                        'board_id': instance.id,
                    },
                )
        except Exception as e:
            pass

    _comment_count.admin_order_field = '_comment_count'
    _like_count.admin_order_field = '_like_count'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'tag_name',
    )
    list_editable = [
        'tag_name',
    ]


@admin.register(BoardGroup)
class BoardGroupAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'group_name',
    )
    list_editable = [
        'group_name',
    ]
