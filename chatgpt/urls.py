from django.urls import path
from .views import *

app_name = 'chatgpt'


urlpatterns = [
    path('post-summary/<int:post_id>', get_summary_by_post_id, name='get_summary_by_post_id'),
]
