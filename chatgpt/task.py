from billiard.exceptions import SoftTimeLimitExceeded
from django.conf import settings
from chatgpt.consts import (
    POST_SUMMARY_SYSTEM_PROMPT,
    ProcessStatus,
)
from chatgpt.models import PostSummary
from chatgpt.services import get_chatgpt_response
from common.common_utils.io_utils import send_email
from common.consts.common_consts import (
    EMAIL_TEMPLATE_MAPPER,
    POST_SUMMARY_ISSUE,
)
from config.celery import app


@app.task(time_limit=30)
def update_post_summary(body: str, post_summary_id: int) -> None:
    try:
        response = get_chatgpt_response(POST_SUMMARY_SYSTEM_PROMPT, body, [])
        post_summary = PostSummary.objects.get(id=post_summary_id)
        post_summary.body = response
        post_summary.status = ProcessStatus.DONE.value
        post_summary.save()
    except PostSummary.DoesNotExist:
        send_email(
            f'[Beany 블로그] Update Post Summary Issue Raised - PostSummary id: {post_summary_id}',
            EMAIL_TEMPLATE_MAPPER[POST_SUMMARY_ISSUE],
            {},
            settings.NOTICE_EMAILS,
        )
    except SoftTimeLimitExceeded:
        post_summary = PostSummary.objects.get(id=post_summary_id)
        post_summary.status = ProcessStatus.FAIL.value
        post_summary.save()
        send_email(
            f'[Beany 블로그] Task Timeout - PostSummary id: {post_summary_id}',
            EMAIL_TEMPLATE_MAPPER[POST_SUMMARY_ISSUE],
            {},
            settings.NOTICE_EMAILS,
        )
