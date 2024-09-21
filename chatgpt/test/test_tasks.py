from django.conf import settings
from django.test import TestCase
from unittest.mock import patch

from accounts.models import User
from board.models import (
    Board,
    Post,
)
from chatgpt.consts import (
    POST_SUMMARY_SYSTEM_PROMPT,
    ProcessStatus,
)
from chatgpt.models import PostSummary
from chatgpt.task import update_post_summary
from common.consts.common_consts import (
    EMAIL_TEMPLATE_MAPPER,
    POST_SUMMARY_ISSUE,
)


class UpdatePostSummaryTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user',
            password='test_password',
        )
        self.board = Board.objects.create(
            url='test_board',
            name='test_board',
        )
        self.active_post = Post.objects.create(
            title="Active Post",
            board=self.board,
            is_active=True,
            author=self.user,
        )
        self.post_summary = PostSummary.objects.create(post_id=self.active_post.id)
        self.body = "New blog post content"
        self.response_body = "Generated summary by ChatGPT"

    @patch('chatgpt.task.get_chatgpt_response')
    def test_update_post_summary_success(self, mock_get_chatgpt_response):
        # Given: ChatGPT의 응답을 모킹합니다.
        mock_get_chatgpt_response.return_value = self.response_body

        # When: update_post_summary 함수를 호출합니다.
        update_post_summary(self.body, self.post_summary.id)

        # Then: PostSummary 객체가 업데이트되었는지 확인합니다.
        self.post_summary.refresh_from_db()
        self.assertEqual(self.post_summary.body, self.response_body)
        self.assertEqual(self.post_summary.status, ProcessStatus.DONE.value)
        mock_get_chatgpt_response.assert_called_once_with(POST_SUMMARY_SYSTEM_PROMPT, self.body, [])

    @patch('chatgpt.task.get_chatgpt_response')
    @patch('chatgpt.task.send_email')
    def test_update_post_summary_does_not_exist(self, mock_send_email, mock_get_chatgpt_response):
        # Given: 존재하지 않는 PostSummary ID를 사용합니다.
        invalid_post_summary_id = 999
        mock_get_chatgpt_response.return_value = self.response_body

        # When: update_post_summary 함수를 호출합니다.
        update_post_summary(self.body, invalid_post_summary_id)

        # Then: PostSummary.DoesNotExist 예외가 발생했을 때 이메일이 전송되는지 확인합니다.
        mock_send_email.assert_called_once_with(
            f'[Beany 블로그] Update Post Summary Issue Raised - PostSummary id: {invalid_post_summary_id}',
            EMAIL_TEMPLATE_MAPPER[POST_SUMMARY_ISSUE],
            {},
            settings.NOTICE_EMAILS,
        )
