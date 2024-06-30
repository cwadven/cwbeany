from django.contrib import admin

from popup.models import HomePopupModal


class HomePopupModalAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'description',
        'on_click_link',
        'sequence',
        'start_time',
        'end_time',
        'is_active',
    ]


admin.site.register(HomePopupModal, HomePopupModalAdmin)
