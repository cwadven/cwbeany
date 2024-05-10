from django.test import TestCase

from accounts.models import User
from board.models import (
    Board,
    BoardGroup,
    Post,
    Tag,
)
from board.services import (
    get_active_posts,
    get_boards_by_board_group_id,
    get_tags,
    get_tags_active_post_count,
)


class GetBoardsByBoardGroupIdTestCase(TestCase):
    def setUp(self):
        self.group1 = BoardGroup.objects.create(group_name='group1')
        self.group2 = BoardGroup.objects.create(group_name='group2')
        self.board1_with_group1 = Board.objects.create(
            url='board1',
            name='board1',
            board_group=self.group1,
        )
        self.board2_with_group1 = Board.objects.create(
            url='board2',
            name='board2',
            board_group=self.group1,
        )
        self.board3_with_group2 = Board.objects.create(
            url='board3',
            name='board3',
            board_group=self.group2,
        )
        self.board4_without_group = Board.objects.create(
            url='board4',
            name='board4',
        )

    def test_get_boards_by_board_group_id_when_board_has_group(self):
        # Given: Board group ids
        given_board_group_ids = [self.group1.id, self.group2.id]
        expected_boards = [
            [self.board1_with_group1, self.board2_with_group1],
            [self.board3_with_group2],
        ]

        for given_board_group_id, expected_board in zip(given_board_group_ids, expected_boards):
            # When: Get boards by board group id
            boards = get_boards_by_board_group_id(given_board_group_id)

            # Then: Boards are returned
            self.assertEqual(boards, expected_board)

    def test_get_boards_by_board_group_id_when_board_group_not_exists(self):
        # Given: Delete all board groups
        Board.objects.all().update(board_group=None)

        # When: Get boards by board group id
        boards = get_boards_by_board_group_id(self.group1.id)

        # Then: No boards are returned
        self.assertEqual(boards, [])


class GetActivePostsTestCase(TestCase):
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
        self.inactive_post = Post.objects.create(
            title="Inactive Post",
            board=self.board,
            is_active=False,
            author=self.user,
        )

    def test_get_active_posts(self):
        # Given:
        # When: Get active posts
        active_posts = get_active_posts()

        # Then: Active posts are returned
        # And: Only active posts are returned
        self.assertEqual(active_posts.count(), 1)
        # And: Active post is returned
        self.assertEqual(active_posts.first().id, self.active_post.id)


class GetTagsTestCase(TestCase):
    def setUp(self):
        # Setting up data for the tests
        self.tag_django = Tag.objects.create(tag_name='Django')
        self.tag_python = Tag.objects.create(tag_name='Python')
        self.tag_api = Tag.objects.create(tag_name='API')

    def test_get_tags(self):
        # Given:
        # When:
        all_tags = get_tags()

        # Then: All tags are returned
        self.assertEqual(all_tags.count(), 3)
        # And: Specific tags are returned
        self.assertEqual(
            set(all_tags.values_list('tag_name', flat=True)),
            {'Django', 'Python', 'API'}
        )


class TagPostCountTestCase(TestCase):
    def setUp(self):
        # Given: User
        self.user = User.objects.create_user(
            username='test_user',
            password='test_password',
        )
        # And: Board
        self.board = Board.objects.create(
            url='test_board',
            name='test_board',
        )
        # And: Tags
        self.tag_django = Tag.objects.create(tag_name='Django')
        self.tag_python = Tag.objects.create(tag_name='Python')
        self.tag_api = Tag.objects.create(tag_name='API')
        # And: Create Posts with Tags
        self.active_post_with_tag_django_python = Post.objects.create(
            title='Active Post',
            board=self.board,
            is_active=True,
            author=self.user,
        )
        self.active_post_with_tag_django_python.tag_set.add(
            self.tag_django,
            self.tag_python,
        )
        self.active_post_with_tag_django_api = Post.objects.create(
            title='Active Post',
            board=self.board,
            is_active=True,
            author=self.user,
        )
        self.active_post_with_tag_django_api.tag_set.add(
            self.tag_django,
            self.tag_api,
        )
        self.inactive_post_with_tag_django_python_api = Post.objects.create(
            title="Inactive Post",
            board=self.board,
            is_active=False,
            author=self.user,
        )
        self.inactive_post_with_tag_django_python_api.tag_set.add(
            self.tag_django,
            self.tag_python,
            self.tag_api,
        )

    def test_active_post_counts(self):
        # Given: Tag IDs
        tag_ids = [self.tag_django.id, self.tag_python.id, self.tag_api.id]

        # When: Get tags active post count
        active_posts_count = get_tags_active_post_count(tag_ids)

        # Then: Active post counts are returned (inactive_post_with_tag_django_python_api not seen)
        # And: active_post_with_tag_django_python, active_post_with_tag_django_api ==> 2
        self.assertEqual(active_posts_count[self.tag_django.id], 2)
        # And: active_post_with_tag_django_python ==> 1
        self.assertEqual(active_posts_count[self.tag_python.id], 1)
        # And: active_post_with_tag_django_api ==> 1
        self.assertEqual(active_posts_count[self.tag_api.id], 1)

    def test_empty_tag_ids(self):
        # Given: Empty tag ids
        tag_ids = []

        # When: Get tags active post count
        active_posts_count = get_tags_active_post_count(tag_ids)

        # Then: Empty dictionary
        self.assertEqual(active_posts_count, {})
