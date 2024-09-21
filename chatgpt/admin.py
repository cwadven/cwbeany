from django.contrib import admin

from chatgpt.models import (
    Lesson,
    LessonInformation,
    PostSummary,
)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'summary',
        'body',
    )


@admin.register(LessonInformation)
class LessonInformationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'summary',
        'system_prompt',
        'prompt',
        'tag',
    )


@admin.register(PostSummary)
class PostSummaryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'body',
        'post',
        'status',
        'created_at',
        'updated_at',
    )
