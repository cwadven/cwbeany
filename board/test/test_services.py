from unittest.mock import patch

from django.test import TestCase

from accounts.models import User
from board.managers import PostQuerySet
from board.models import (
    Board,
    BoardGroup,
    Like,
    Post,
    Reply,
    Rereply,
    Tag,
)
from board.services import (
    get_active_filtered_posts,
    get_active_posts,
    get_board_paged_posts,
    get_boards_by_board_group_id,
    get_tags,
    get_tags_active_post_count,
    update_post_like_count,
    update_post_reply_count,
    update_post_rereply_count,
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


class PostUpdateReplyCountTestCase(TestCase):
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
        # And: Create Posts with Tags
        self.active_post = Post.objects.create(
            title='Active Post',
            board=self.board,
            is_active=True,
            author=self.user,
        )
        self.reply1 = Reply.objects.create(body='Reply 1', post=self.active_post, author=self.user)
        self.reply2 = Reply.objects.create(body='Reply 2', post=self.active_post, author=self.user)

    def test_update_post_reply_count_post_not_exists(self):
        # Given: Post not exists
        post_id = 0

        # When: Update post Reply count
        update_post_reply_count(post_id)

        # Then:
        # Noting happens

    def test_update_post_reply_count(self):
        # Given: Test before update
        self.assertEqual(self.active_post.reply_count, 0)

        # When: Update post reply count
        update_post_reply_count(self.active_post.id)

        # Then: Post is updated
        self.active_post.refresh_from_db()
        # And: Reply count is updated
        self.assertEqual(self.active_post.reply_count, 2)

    def test_update_with_no_replies(self):
        # Given: Test before update
        no_reply_post = Post.objects.create(
            title='Active Post',
            board=self.board,
            is_active=True,
            author=self.user,
        )
        self.assertEqual(no_reply_post.reply_count, 0)

        # When: Update post reply count
        update_post_reply_count(no_reply_post.id)

        # Then: Post is updated
        no_reply_post.refresh_from_db()
        # And: Reply count is updated
        self.assertEqual(no_reply_post.reply_count, 0)


class PostUpdateRereplyCountTestCase(TestCase):
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
        # And: Create Posts with Tags
        self.active_post = Post.objects.create(
            title='Active Post',
            board=self.board,
            is_active=True,
            author=self.user,
        )
        self.reply1 = Reply.objects.create(body='Reply 1', post=self.active_post, author=self.user)
        self.reply1_rereply1 = Rereply.objects.create(
            post=self.active_post,
            reply=self.reply1,
            body='Rereply 1',
            author=self.user,
        )
        self.reply1_rereply2 = Rereply.objects.create(
            post=self.active_post,
            reply=self.reply1,
            body='Rereply 2',
            author=self.user,
        )

    def test_update_post_rereply_count_post_not_exists(self):
        # Given: Post not exists
        post_id = 0

        # When: Update post Rereply count
        update_post_rereply_count(post_id)

        # Then:
        # Noting happens

    def test_update_post_rereply_count(self):
        # Given: Test before update
        self.assertEqual(self.active_post.rereply_count, 0)

        # When: Update post Rereply count
        update_post_rereply_count(self.active_post.id)

        # Then: Post is updated
        self.active_post.refresh_from_db()
        # And: Rereply count is updated
        self.assertEqual(self.active_post.rereply_count, 2)

    def test_update_with_no_rereplies(self):
        # Given: Test before update
        no_reply_post = Post.objects.create(
            title='Active Post',
            board=self.board,
            is_active=True,
            author=self.user,
        )
        self.assertEqual(no_reply_post.rereply_count, 0)

        # When: Update post Rereply count
        update_post_rereply_count(no_reply_post.id)

        # Then: Post is updated
        no_reply_post.refresh_from_db()
        # And: Rereply count is updated
        self.assertEqual(no_reply_post.rereply_count, 0)


class PostUpdateLikeCountTestCase(TestCase):
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
        # And: Create Posts with Tags
        self.active_post = Post.objects.create(
            title='Active Post',
            board=self.board,
            is_active=True,
            author=self.user,
        )
        self.like1 = Like.objects.create(post=self.active_post, author=self.user)
        self.like2 = Like.objects.create(post=self.active_post, author=self.user)

    def test_update_post_like_count_post_not_exists(self):
        # Given: Post not exists
        post_id = 0

        # When: Update post Like count
        update_post_like_count(post_id)

        # Then:
        # Noting happens

    def test_update_post_like_count(self):
        # Given: Test before update
        self.assertEqual(self.active_post.like_count, 0)

        # When: Update post Like count
        update_post_like_count(self.active_post.id)

        # Then: Post is updated
        self.active_post.refresh_from_db()
        # And: Like count is updated
        self.assertEqual(self.active_post.like_count, 2)

    def test_update_with_no_likes(self):
        # Given: Test before update
        no_reply_post = Post.objects.create(
            title='Active Post',
            board=self.board,
            is_active=True,
            author=self.user,
        )
        self.assertEqual(no_reply_post.like_count, 0)

        # When: Update post Like count
        update_post_like_count(no_reply_post.id)

        # Then: Post is updated
        no_reply_post.refresh_from_db()
        # And: Like count is updated
        self.assertEqual(no_reply_post.like_count, 0)


class GetActiveFilteredPostsTestCase(TestCase):
    def setUp(self):
        # Create User
        self.user = User.objects.create_user(
            username='test_user',
            password='test_password',
        )
        # Create Boards
        self.django_board = Board.objects.create(
            url='django',
            name='django',
        )
        self.spring_board = Board.objects.create(
            url='spring',
            name='spring',
        )
        # Create Tags
        self.python_tag = Tag.objects.create(tag_name='python')
        self.java_tag = Tag.objects.create(tag_name='java')
        # Create Posts
        self.active_django_post = Post.objects.create(
            title='Active Django post',
            board=self.django_board,
            is_active=True,
            author=self.user,
        )
        self.inactive_django_post = Post.objects.create(
            title='Inactive Django post',
            board=self.django_board,
            is_active=False,
            author=self.user,
        )
        self.active_spring_post = Post.objects.create(
            title='Active Spring post',
            board=self.spring_board,
            is_active=True,
            author=self.user,
        )
        self.inactive_spring_post = Post.objects.create(
            title='Inactive Spring post',
            board=self.spring_board,
            is_active=False,
            author=self.user,
        )
        # Add tags to posts
        self.active_django_post.tag_set.add(self.python_tag)
        self.active_spring_post.tag_set.add(self.java_tag)

    def test_filter_by_search_title(self):
        # Given: Search keyword
        search = 'django'

        # When: Filter by search
        results = get_active_filtered_posts(search=search)

        # Then: Active Django post is returned
        self.assertEquals(results.count(), 1)
        self.assertEquals(results[0].id, self.active_django_post.id)

    def test_filter_by_search_body(self):
        # Given: Search keyword
        search = 'hello'
        # And: Add search keyword to body
        self.active_spring_post.body = 'my friend Hello'
        self.active_spring_post.save()

        # When: Filter by search
        results = get_active_filtered_posts(search=search)

        # Then: Active Spring post is returned
        self.assertEquals(results.count(), 1)
        self.assertEquals(results[0].id, self.active_spring_post.id)

    def test_filter_by_board_urls(self):
        # Given: Board urls
        board_urls = ['django']

        # When: Filter by board urls
        results = get_active_filtered_posts(board_urls=board_urls)

        # Then: Active Django post is returned
        self.assertEquals(results.count(), 1)
        self.assertEquals(results[0].id, self.active_django_post.id)

    def test_filter_by_tag_names(self):
        # Given: Tag names
        tag_names = ['python']

        # When Filter by tag names
        results = get_active_filtered_posts(tag_names=tag_names)

        # Then: Active Django post is returned due to tag has python
        self.assertEquals(results.count(), 1)
        self.assertEquals(results[0].id, self.active_django_post.id)

    def test_filter_by_multiple_criteria(self):
        # Given: Search keyword
        search = 'aaa'
        # And: Add search keyword to body
        self.active_spring_post.body = 'my friend Hello aaa'
        self.active_spring_post.save()
        # And: Search Board urls
        board_urls = ['spring']
        # And: Search Tag names
        tag_names = ['java']

        # When: Filter by multiple criteria
        results = get_active_filtered_posts(search=search, board_urls=board_urls, tag_names=tag_names)

        # Then: Active Spring post
        self.assertEquals(results.count(), 1)
        self.assertEquals(results[0].id, self.active_spring_post.id)

    def test_no_filters(self):
        # Given: No filters
        # When: get_active_filtered_posts is called
        results = get_active_filtered_posts()

        # Then: All active posts are returned
        self.assertEquals(results.count(), 2)
        self.assertEquals(
            set(results.values_list('id', flat=True)),
            {self.active_django_post.id, self.active_spring_post.id},
        )


class GetBoardPagedPostsTest(TestCase):
    def setUp(self):
        # Create User
        self.user = User.objects.create_user(
            username='test_user',
            password='test_password',
        )
        # Create Boards
        self.django_board = Board.objects.create(
            url='django',
            name='django',
        )
        self.spring_board = Board.objects.create(
            url='spring',
            name='spring',
        )
        # Create Tags
        self.python_tag = Tag.objects.create(tag_name='python')
        self.java_tag = Tag.objects.create(tag_name='java')
        # Create Posts
        self.active_django_post = Post.objects.create(
            title='Active Django post',
            board=self.django_board,
            is_active=True,
            author=self.user,
        )
        self.inactive_django_post = Post.objects.create(
            title='Inactive Django post',
            board=self.django_board,
            is_active=False,
            author=self.user,
        )
        self.active_spring_post = Post.objects.create(
            title='Active Spring post',
            board=self.spring_board,
            is_active=True,
            author=self.user,
        )
        self.inactive_spring_post = Post.objects.create(
            title='Inactive Spring post',
            board=self.spring_board,
            is_active=False,
            author=self.user,
        )
        # Add tags to posts
        self.active_django_post.tag_set.add(self.python_tag)
        self.active_spring_post.tag_set.add(self.java_tag)

    @patch('board.services.web_paging')
    @patch('board.services.get_active_filtered_posts')
    def test_get_board_paged_posts(self,
                                   mock_get_active_filtered_posts,
                                   mock_web_paging):
        # Given: Search keyword
        search = 'django'
        # And: Board urls
        board_urls = ['django']
        # And: Tag names
        tag_names = ['python']
        # And: Page
        page = 1
        # And: Mock get_active_filtered_posts
        mock_get_active_filtered_posts.return_value = Post.objects.filter(
            id=self.active_django_post.id
        )

        # When: Get board paged posts
        get_board_paged_posts(
            search=search,
            board_urls=board_urls,
            tag_names=tag_names,
            page=page,
        )

        # Then: get_active_filtered_posts and web_paging is called
        mock_get_active_filtered_posts.assert_called_once_with(
            search=search,
            board_urls=board_urls,
            tag_names=tag_names,
        )
        called_args, _ = mock_web_paging.call_args
        self.assertIsInstance(called_args[0], PostQuerySet)
        self.assertEqual(called_args[1], page)
        self.assertEqual(called_args[2], 10)
        self.assertEqual(called_args[3], 5)
