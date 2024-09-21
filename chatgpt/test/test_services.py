from django.test import TestCase
from django.utils import timezone

from accounts.models import User
from board.models import (
    Board,
    Post,
)
from chatgpt.models import (
    Lesson,
    PostSummary,
)
from chatgpt.services import (
    get_lessons,
    get_latest_post_summary_by_post_id,
)


class GetAnnouncesTestCase(TestCase):
    def setUp(self):
        self.lesson1 = Lesson.objects.create(
            summary='test1',
            body='test1',
        )
        self.lesson2 = Lesson.objects.create(
            summary='test2',
            body='test2',
        )
        self.lesson3 = Lesson.objects.create(
            summary='test3',
            body='test3',
        )

    def test_get_lessons(self):
        # Given:
        # When:
        all_lessons = get_lessons()

        # Then: All lessons are returned
        self.assertEqual(all_lessons.count(), 3)
        # And: Specific lessons are returned
        self.assertEqual(
            set(all_lessons.values_list('id', flat=True)),
            {self.lesson1.id, self.lesson2.id, self.lesson3.id}
        )


class GetLatestPostSummaryTest(TestCase):

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
        self.old_post_summary = PostSummary.objects.create(
            post_id=self.active_post.id,
            body="Old summary",
            created_at=timezone.now() - timezone.timedelta(days=2)
        )
        self.new_post_summary = PostSummary.objects.create(
            post_id=self.active_post.id,
            body="New summary",
            created_at=timezone.now() - timezone.timedelta(days=1)
        )

    def test_get_latest_post_summary_by_post_id_returns_latest_summary(self):
        # When: get_latest_post_summary_by_post_id 함수를 호출합니다.
        result = get_latest_post_summary_by_post_id(self.active_post.id)

        # Then: 가장 최근에 생성된 PostSummary가 반환되는지 확인합니다.
        self.assertEqual(result, self.new_post_summary)

    def test_get_latest_post_summary_by_post_id_returns_none_if_no_summaries_exist(self):
        # Given: 존재하지 않는 post_id를 사용합니다.
        non_existing_post_id = 999

        # When: get_latest_post_summary_by_post_id 함수를 호출합니다.
        result = get_latest_post_summary_by_post_id(non_existing_post_id)

        # Then: 결과가 None인지 확인합니다.
        self.assertEqual(result, None)
