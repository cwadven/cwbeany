import json
from unittest.mock import patch, call

from django.test import (
    Client,
    TestCase,
)
from django.urls import reverse

from accounts.models import User
from board.documents import PostDocument
from board.models import (
    Board,
    BoardGroup,
    Post,
    Tag,
)


class BoardGroupTestCase(TestCase):
    def setUp(self):
        # 테스트에 필요한 데이터 세팅
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
        self.url = reverse(
            'board:get_boards_info_from_board_group',
            args=[self.group1.id],
        )

    @staticmethod
    def _create_url(group_id: int):
        return reverse(
            'board:get_boards_info_from_board_group',
            args=[group_id],
        )

    def test_get_boards_info_from_board_group_with_existing_group(self):
        # Given: 그룹1에 속한 게시판들을 조회하는 요청 데이터
        url = self._create_url(self.group1.id)

        # When: HTTP GET 요청
        response = self.client.get(url)
        content = json.loads(response.content.decode())

        # Then: HTTP 응답
        self.assertEqual(response.status_code, 200)
        # And: 응답 데이터 검증
        self.assertEqual(
            content,
            {
                'board_set': [
                    {
                        'name': self.board1_with_group1.name,
                        'url': self.board1_with_group1.url,
                    },
                    {
                        'name': self.board2_with_group1.name,
                        'url': self.board2_with_group1.url,
                    },
                ]
            },
        )

    def test_get_boards_info_from_board_group_without_existing_group(self):
        # Given: 그룹을 전부 없앰
        Board.objects.all().update(board_group=None)
        # And: 그룹1에 속한 게시판들을 조회하는 요청 데이터
        url = self._create_url(self.group1.id)

        # When: HTTP GET 요청
        response = self.client.get(url)
        content = json.loads(response.content.decode())

        # Then: HTTP 응답
        self.assertEqual(response.status_code, 200)
        # And: 응답 데이터 검증
        self.assertEqual(
            content,
            {
                'board_set': []
            },
        )


class GetBoardPostsTest(TestCase):
    def setUp(self):
        # Given: 테스트에 필요한 데이터 세팅
        self.client = Client()
        # And: 유저, 게시판, 게시물 생성
        self.user = User.objects.create_user(
            username='test_user',
            password='test_password',
        )
        self.board = Board.objects.create(
            url='test-board',
            name='Test Board',
            info='Some info',
            name_background_color='#FFFFFF',
            name_text_color='#000000',
            info_background_color='#FFFFFF',
            info_text_color='#000000'
        )
        self.post1 = Post.objects.create(
            title='Post 1',
            body='Body 1',
            board=self.board,
            author=self.user,
        )
        self.post2 = Post.objects.create(
            title='Post 2',
            body='Body 2',
            board=self.board,
            author=self.user,
        )
        self.view_name = 'board:get_board_posts'

    @patch('board.views.BoardPostsResponse')
    @patch('board.views.BoardPost')
    @patch('board.views.BoardDetailInfo')
    @patch('board.views.get_board_paged_elastic_posts')
    def test_get_board_posts_with_search(
            self,
            mock_get_board_paged_elastic_posts,
            mock_board_detail_info,
            mock_board_post,
            mock_board_posts_response,
    ):
        # Given: 검색어 'Post 1'
        search = 'Post 1'
        # And: Set Post 1 data
        self.post1.post_img = 'test.jpg'
        self.post1.reply_count = 3
        self.post1.rereply_count = 2
        self.post1.body = 'T ' * 100
        self.post1.save()
        # And: mock get_board_paged_elastic_posts
        post_document = PostDocument()
        doc1 = post_document.prepare(self.post1)
        post_doc1 = PostDocument(meta={'id': self.post1.id}, **doc1)
        doc2 = post_document.prepare(self.post2)
        post_doc2 = PostDocument(meta={'id': self.post2.id}, **doc2)
        mock_get_board_paged_elastic_posts.return_value = {
            'page_posts': [post_doc1, post_doc2],
            'page_range': [1],
            'has_previous': False,
            'has_next': False,
            'total_pages': 1,
            'total_count': 2,
            'previous_page_number': None,
            'next_page_number': None,
            'num_pages': 1,
            'current_page': 1,
        }
        # And: model_dump 응답
        mock_board_posts_response.return_value.model_dump.return_value = {}

        # When: HTTP GET 요청
        response = self.client.get(
            reverse(
                self.view_name,
                kwargs={'board_url': 'test-board'}),
            {'search': search},
        )

        # Then: HTTP 응답
        self.assertEqual(response.status_code, 200)
        # And: 유효한 HTML 파일
        self.assertTemplateUsed(response, 'board/board_detail.html')
        # And: get_board_paged_elastic_posts called
        mock_get_board_paged_elastic_posts.assert_called_once_with(
            board_urls=['test-board'],
            search=search,
            page=1,
        )
        # And: BoardDetailInfo called
        mock_board_detail_info.assert_called_once_with(
            board_img_url=None,
            name='Test Board',
            info='Some info',
            url='test-board',
            info_background_color='#FFFFFF',
            info_text_color='#000000',
            name_background_color='#FFFFFF',
            name_text_color='#000000',
        )
        # And: BoardPost called with first
        mock_board_post.assert_has_calls(
            [
                call(
                    id=post_doc1.id,
                    title=post_doc1.title,
                    short_body='T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T',
                    board_url=post_doc1.board.url,
                    author_nickname=post_doc1.author.nickname,
                    created_at=post_doc1.created_at.strftime('%Y-%m-%d'),
                    like_count=post_doc1.like_count,
                    reply_count=5,
                    image_url='/media/test.jpg',
                ),
                call(
                    id=post_doc2.id,
                    title=post_doc2.title,
                    short_body=post_doc2.body,
                    board_url=post_doc2.board.url,
                    author_nickname=post_doc2.author.nickname,
                    created_at=post_doc2.created_at.strftime('%Y-%m-%d'),
                    like_count=post_doc2.like_count,
                    reply_count=post_doc2.reply_count,
                    image_url='/static/logo.ico',
                ),
            ]
        )
        mock_board_posts_response.assert_called_once_with(
            board_detail_info=mock_board_detail_info.return_value,
            posts=[mock_board_post.return_value, mock_board_post.return_value],
            has_previous=False,
            has_next=False,
            previous_page_number=None,
            current_page_number=1,
            next_page_number=None,
            last_page_number=1,
            page_range=[1],
        )

    @patch('board.views.BoardPostsResponse')
    @patch('board.views.BoardPost')
    @patch('board.views.BoardDetailInfo')
    @patch('board.views.get_board_paged_elastic_posts')
    def test_get_board_posts_no_search(
            self,
            mock_get_board_paged_elastic_posts,
            mock_board_detail_info,
            mock_board_post,
            mock_board_posts_response,
    ):
        # Given: 검색어 없음
        # And: Set Post 1 data
        self.post1.post_img = 'test.jpg'
        self.post1.reply_count = 3
        self.post1.rereply_count = 2
        self.post1.body = 'T ' * 100
        self.post1.save()
        # And: mock get_board_paged_elastic_posts
        post_document = PostDocument()
        doc1 = post_document.prepare(self.post1)
        post_doc1 = PostDocument(meta={'id': self.post1.id}, **doc1)
        doc2 = post_document.prepare(self.post2)
        post_doc2 = PostDocument(meta={'id': self.post2.id}, **doc2)
        mock_get_board_paged_elastic_posts.return_value = {
            'page_posts': [post_doc1, post_doc2],
            'page_range': [1],
            'has_previous': False,
            'has_next': False,
            'total_pages': 1,
            'total_count': 2,
            'previous_page_number': None,
            'next_page_number': None,
            'num_pages': 1,
            'current_page': 1,
        }
        # And: model_dump 응답
        mock_board_posts_response.return_value.model_dump.return_value = {}

        # When: HTTP GET 요청
        response = self.client.get(reverse(self.view_name, kwargs={'board_url': 'test-board'}))

        # Then: HTTP 응답
        self.assertEqual(response.status_code, 200)
        # And: 유효한 HTML 파일
        self.assertTemplateUsed(response, 'board/board_detail.html')
        # And: get_board_paged_elastic_posts called
        mock_get_board_paged_elastic_posts.assert_called_once_with(
            board_urls=['test-board'],
            search=None,
            page=1,
        )
        # And: BoardDetailInfo called
        mock_board_detail_info.assert_called_once_with(
            board_img_url=None,
            name='Test Board',
            info='Some info',
            url='test-board',
            info_background_color='#FFFFFF',
            info_text_color='#000000',
            name_background_color='#FFFFFF',
            name_text_color='#000000',
        )
        # And: BoardPost called with first
        mock_board_post.assert_has_calls(
            [
                call(
                    id=post_doc1.id,
                    title=post_doc1.title,
                    short_body='T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T',
                    board_url=post_doc1.board.url,
                    author_nickname=post_doc1.author.nickname,
                    created_at=post_doc1.created_at.strftime('%Y-%m-%d'),
                    like_count=post_doc1.like_count,
                    reply_count=5,
                    image_url='/media/test.jpg',
                ),
                call(
                    id=post_doc2.id,
                    title=post_doc2.title,
                    short_body=post_doc2.body,
                    board_url=post_doc2.board.url,
                    author_nickname=post_doc2.author.nickname,
                    created_at=post_doc2.created_at.strftime('%Y-%m-%d'),
                    like_count=post_doc2.like_count,
                    reply_count=post_doc2.reply_count,
                    image_url='/static/logo.ico',
                ),
            ]
        )
        mock_board_posts_response.assert_called_once_with(
            board_detail_info=mock_board_detail_info.return_value,
            posts=[mock_board_post.return_value, mock_board_post.return_value],
            has_previous=False,
            has_next=False,
            previous_page_number=None,
            current_page_number=1,
            next_page_number=None,
            last_page_number=1,
            page_range=[1],
        )

    def test_get_board_posts_nonexistent_board(self):
        # Given: 존재하지 않는 게시판
        board_url = 'nonexistent-board'

        # When: HTTP GET 요청
        response = self.client.get(reverse(self.view_name, kwargs={'board_url': board_url}))

        # Then: HTTP 응답
        self.assertEqual(response.status_code, 404)


class GetAllBoardPostsTest(TestCase):
    def setUp(self):
        # Given: 테스트에 필요한 데이터 세팅
        self.client = Client()
        # And: 유저, 게시판, 게시물 생성
        self.user = User.objects.create_user(
            username='test_user',
            password='test_password',
        )
        self.board = Board.objects.create(
            url='test-board',
            name='Test Board',
            info='Some info',
            name_background_color='#FFFFFF',
            name_text_color='#000000',
            info_background_color='#FFFFFF',
            info_text_color='#000000'
        )
        self.post1 = Post.objects.create(
            title='Post 1',
            body='Body 1',
            board=self.board,
            author=self.user,
        )
        self.post2 = Post.objects.create(
            title='Post 2',
            body='Body 2',
            board=self.board,
            author=self.user,
        )
        self.view_name = 'board:all_board_posts'

    @patch('board.views.BoardPostsResponse')
    @patch('board.views.BoardPost')
    @patch('board.views.BoardDetailInfo')
    @patch('board.views.get_board_paged_elastic_posts')
    def test_get_all_board_posts_with_search(
            self,
            mock_get_board_paged_elastic_posts,
            mock_board_detail_info,
            mock_board_post,
            mock_board_posts_response,
    ):
        # Given: 검색어 'Post 1'
        search = 'Post 1'
        # And: Set Post 1 data
        self.post1.post_img = 'test.jpg'
        self.post1.reply_count = 3
        self.post1.rereply_count = 2
        self.post1.body = 'T ' * 100
        self.post1.save()
        # And: mock get_board_paged_elastic_posts
        post_document = PostDocument()
        doc1 = post_document.prepare(self.post1)
        post_doc1 = PostDocument(meta={'id': self.post1.id}, **doc1)
        doc2 = post_document.prepare(self.post2)
        post_doc2 = PostDocument(meta={'id': self.post2.id}, **doc2)
        mock_get_board_paged_elastic_posts.return_value = {
            'page_posts': [post_doc1, post_doc2],
            'page_range': [1],
            'has_previous': False,
            'has_next': False,
            'total_pages': 1,
            'total_count': 2,
            'previous_page_number': None,
            'next_page_number': None,
            'num_pages': 1,
            'current_page': 1,
        }
        # And: model_dump 응답
        mock_board_posts_response.return_value.model_dump.return_value = {}

        # When: HTTP GET 요청
        response = self.client.get(
            reverse(
                self.view_name
            ),
            {'search': search},
        )

        # Then: HTTP 응답
        self.assertEqual(response.status_code, 200)
        # And: 유효한 HTML 파일
        self.assertTemplateUsed(response, 'board/all_board_detail.html')
        # And: get_board_paged_elastic_posts called
        mock_get_board_paged_elastic_posts.assert_called_once_with(
            search=search,
            page=1,
        )
        # And: BoardDetailInfo called
        mock_board_detail_info.assert_called_once_with(
            name=search,
            info=search,
            url=search,
        )
        # And: BoardPost called with first
        mock_board_post.assert_has_calls(
            [
                call(
                    id=post_doc1.id,
                    title=post_doc1.title,
                    short_body='T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T',
                    board_url=post_doc1.board.url,
                    author_nickname=post_doc1.author.nickname,
                    created_at=post_doc1.created_at.strftime('%Y-%m-%d'),
                    like_count=post_doc1.like_count,
                    reply_count=5,
                    image_url='/media/test.jpg',
                ),
                call(
                    id=post_doc2.id,
                    title=post_doc2.title,
                    short_body=post_doc2.body,
                    board_url=post_doc2.board.url,
                    author_nickname=post_doc2.author.nickname,
                    created_at=post_doc2.created_at.strftime('%Y-%m-%d'),
                    like_count=post_doc2.like_count,
                    reply_count=post_doc2.reply_count,
                    image_url='/static/logo.ico',
                ),
            ]
        )
        mock_board_posts_response.assert_called_once_with(
            board_detail_info=mock_board_detail_info.return_value,
            posts=[mock_board_post.return_value, mock_board_post.return_value],
            has_previous=False,
            has_next=False,
            previous_page_number=None,
            current_page_number=1,
            next_page_number=None,
            last_page_number=1,
            page_range=[1],
        )

    @patch('board.views.BoardPostsResponse')
    @patch('board.views.BoardPost')
    @patch('board.views.BoardDetailInfo')
    @patch('board.views.get_board_paged_elastic_posts')
    def test_get_all_board_posts_no_search(
            self,
            mock_get_board_paged_elastic_posts,
            mock_board_detail_info,
            mock_board_post,
            mock_board_posts_response,
    ):
        # Given: 검색어 없음
        # And: Set Post 1 data
        self.post1.post_img = 'test.jpg'
        self.post1.reply_count = 3
        self.post1.rereply_count = 2
        self.post1.body = 'T ' * 100
        self.post1.save()
        # And: mock get_board_paged_elastic_posts
        post_document = PostDocument()
        doc1 = post_document.prepare(self.post1)
        post_doc1 = PostDocument(meta={'id': self.post1.id}, **doc1)
        doc2 = post_document.prepare(self.post2)
        post_doc2 = PostDocument(meta={'id': self.post2.id}, **doc2)
        mock_get_board_paged_elastic_posts.return_value = {
            'page_posts': [post_doc1, post_doc2],
            'page_range': [1],
            'has_previous': False,
            'has_next': False,
            'total_pages': 1,
            'total_count': 2,
            'previous_page_number': None,
            'next_page_number': None,
            'num_pages': 1,
            'current_page': 1,
        }
        # And: model_dump 응답
        mock_board_posts_response.return_value.model_dump.return_value = {}

        # When: HTTP GET 요청
        response = self.client.get(reverse(self.view_name))

        # Then: HTTP 응답
        self.assertEqual(response.status_code, 200)
        # And: 유효한 HTML 파일
        self.assertTemplateUsed(response, 'board/all_board_detail.html')
        # And: get_board_paged_elastic_posts called
        mock_get_board_paged_elastic_posts.assert_called_once_with(
            search=None,
            page=1,
        )
        # And: BoardDetailInfo called
        mock_board_detail_info.assert_called_once_with(
            name='전체 게시판',
            info='전체 게시판',
            url='전체 게시판',
        )
        # And: BoardPost called with first
        mock_board_post.assert_has_calls(
            [
                call(
                    id=post_doc1.id,
                    title=post_doc1.title,
                    short_body='T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T',
                    board_url=post_doc1.board.url,
                    author_nickname=post_doc1.author.nickname,
                    created_at=post_doc1.created_at.strftime('%Y-%m-%d'),
                    like_count=post_doc1.like_count,
                    reply_count=5,
                    image_url='/media/test.jpg',
                ),
                call(
                    id=post_doc2.id,
                    title=post_doc2.title,
                    short_body=post_doc2.body,
                    board_url=post_doc2.board.url,
                    author_nickname=post_doc2.author.nickname,
                    created_at=post_doc2.created_at.strftime('%Y-%m-%d'),
                    like_count=post_doc2.like_count,
                    reply_count=post_doc2.reply_count,
                    image_url='/static/logo.ico',
                ),
            ]
        )
        mock_board_posts_response.assert_called_once_with(
            board_detail_info=mock_board_detail_info.return_value,
            posts=[mock_board_post.return_value, mock_board_post.return_value],
            has_previous=False,
            has_next=False,
            previous_page_number=None,
            current_page_number=1,
            next_page_number=None,
            last_page_number=1,
            page_range=[1],
        )


class GetTaggedPostsTest(TestCase):
    def setUp(self):
        # Given: 테스트에 필요한 데이터 세팅
        self.client = Client()
        # And: 유저, 게시판, 게시물 생성
        self.user = User.objects.create_user(
            username='test_user',
            password='test_password',
        )
        self.board = Board.objects.create(
            url='test-board',
            name='Test Board',
            info='Some info',
            name_background_color='#FFFFFF',
            name_text_color='#000000',
            info_background_color='#FFFFFF',
            info_text_color='#000000'
        )
        self.post1 = Post.objects.create(
            title='Post 1',
            body='Body 1',
            board=self.board,
            author=self.user,
        )
        self.post2 = Post.objects.create(
            title='Post 2',
            body='Body 2',
            board=self.board,
            author=self.user,
        )
        # And: 태그 생성
        self.tag1 = Tag.objects.create(tag_name='tag1')
        self.tag2 = Tag.objects.create(tag_name='tag2')
        self.post1.tag_set.add(self.tag1)
        self.post2.tag_set.add(self.tag2)
        self.view_name = 'board:get_tagged_posts'

    @patch('board.views.BoardPostsResponse')
    @patch('board.views.BoardPost')
    @patch('board.views.BoardDetailInfo')
    @patch('board.views.get_board_paged_elastic_posts')
    def test_get_tagged_posts_with_search(
            self,
            mock_get_board_paged_elastic_posts,
            mock_board_detail_info,
            mock_board_post,
            mock_board_posts_response,
    ):
        # Given: 검색어 'Post'
        search = 'Post'
        # And: Set Post 1 data
        self.post1.post_img = 'test.jpg'
        self.post1.reply_count = 3
        self.post1.rereply_count = 2
        self.post1.body = 'T ' * 100
        self.post1.save()
        # And: mock get_board_paged_elastic_posts
        post_document = PostDocument()
        doc1 = post_document.prepare(self.post1)
        post_doc1 = PostDocument(meta={'id': self.post1.id}, **doc1)
        doc2 = post_document.prepare(self.post2)
        post_doc2 = PostDocument(meta={'id': self.post2.id}, **doc2)
        mock_get_board_paged_elastic_posts.return_value = {
            'page_posts': [post_doc1, post_doc2],
            'page_range': [1],
            'has_previous': False,
            'has_next': False,
            'total_pages': 1,
            'total_count': 2,
            'previous_page_number': None,
            'next_page_number': None,
            'num_pages': 1,
            'current_page': 1,
        }
        # And: model_dump 응답
        mock_board_posts_response.return_value.model_dump.return_value = {}

        # When: HTTP GET 요청
        response = self.client.get(
            reverse(
                self.view_name,
                kwargs={'tag_name': self.tag1.tag_name}),
            {'search': search},
        )

        # Then: HTTP 응답
        self.assertEqual(response.status_code, 200)
        # And: 유효한 HTML 파일
        self.assertTemplateUsed(response, 'board/tagged_board_detail.html')
        # And: get_board_paged_elastic_posts called
        mock_get_board_paged_elastic_posts.assert_called_once_with(
            tag_ids=[self.tag1.id],
            search=search,
            page=1,
        )
        # And: BoardDetailInfo called
        mock_board_detail_info.assert_called_once_with(
            name='tag1',
            info='tag1',
            url='tag1',
        )
        # And: BoardPost called with first
        mock_board_post.assert_has_calls(
            [
                call(
                    id=post_doc1.id,
                    title=post_doc1.title,
                    short_body='T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T',
                    board_url=post_doc1.board.url,
                    author_nickname=post_doc1.author.nickname,
                    created_at=post_doc1.created_at.strftime('%Y-%m-%d'),
                    like_count=post_doc1.like_count,
                    reply_count=5,
                    image_url='/media/test.jpg',
                ),
                call(
                    id=post_doc2.id,
                    title=post_doc2.title,
                    short_body=post_doc2.body,
                    board_url=post_doc2.board.url,
                    author_nickname=post_doc2.author.nickname,
                    created_at=post_doc2.created_at.strftime('%Y-%m-%d'),
                    like_count=post_doc2.like_count,
                    reply_count=post_doc2.reply_count,
                    image_url='/static/logo.ico',
                ),
            ]
        )
        mock_board_posts_response.assert_called_once_with(
            board_detail_info=mock_board_detail_info.return_value,
            posts=[mock_board_post.return_value, mock_board_post.return_value],
            has_previous=False,
            has_next=False,
            previous_page_number=None,
            current_page_number=1,
            next_page_number=None,
            last_page_number=1,
            page_range=[1],
        )

    @patch('board.views.BoardPostsResponse')
    @patch('board.views.BoardPost')
    @patch('board.views.BoardDetailInfo')
    @patch('board.views.get_board_paged_elastic_posts')
    def test_get_tagged_posts_no_search(
            self,
            mock_get_board_paged_elastic_posts,
            mock_board_detail_info,
            mock_board_post,
            mock_board_posts_response,
    ):
        # Given: 검색어 없음
        # And: Set Post 1 data
        self.post1.post_img = 'test.jpg'
        self.post1.reply_count = 3
        self.post1.rereply_count = 2
        self.post1.body = 'T ' * 100
        self.post1.save()
        # And: mock get_board_paged_elastic_posts
        post_document = PostDocument()
        doc1 = post_document.prepare(self.post1)
        post_doc1 = PostDocument(meta={'id': self.post1.id}, **doc1)
        doc2 = post_document.prepare(self.post2)
        post_doc2 = PostDocument(meta={'id': self.post2.id}, **doc2)
        mock_get_board_paged_elastic_posts.return_value = {
            'page_posts': [post_doc1, post_doc2],
            'page_range': [1],
            'has_previous': False,
            'has_next': False,
            'total_pages': 1,
            'total_count': 2,
            'previous_page_number': None,
            'next_page_number': None,
            'num_pages': 1,
            'current_page': 1,
        }
        # And: model_dump 응답
        mock_board_posts_response.return_value.model_dump.return_value = {}

        # When: HTTP GET 요청
        response = self.client.get(
            reverse(
                self.view_name,
                kwargs={'tag_name': self.tag1.tag_name},
            )
        )

        # Then: HTTP 응답
        self.assertEqual(response.status_code, 200)
        # And: 유효한 HTML 파일
        self.assertTemplateUsed(response, 'board/tagged_board_detail.html')
        # And: get_board_paged_elastic_posts called
        mock_get_board_paged_elastic_posts.assert_called_once_with(
            tag_ids=[self.tag1.id],
            search=None,
            page=1,
        )
        # And: BoardDetailInfo called
        mock_board_detail_info.assert_called_once_with(
            name='tag1',
            info='tag1',
            url='tag1',
        )
        # And: BoardPost called with first
        mock_board_post.assert_has_calls(
            [
                call(
                    id=post_doc1.id,
                    title=post_doc1.title,
                    short_body='T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T T',
                    board_url=post_doc1.board.url,
                    author_nickname=post_doc1.author.nickname,
                    created_at=post_doc1.created_at.strftime('%Y-%m-%d'),
                    like_count=post_doc1.like_count,
                    reply_count=5,
                    image_url='/media/test.jpg',
                ),
                call(
                    id=post_doc2.id,
                    title=post_doc2.title,
                    short_body=post_doc2.body,
                    board_url=post_doc2.board.url,
                    author_nickname=post_doc2.author.nickname,
                    created_at=post_doc2.created_at.strftime('%Y-%m-%d'),
                    like_count=post_doc2.like_count,
                    reply_count=post_doc2.reply_count,
                    image_url='/static/logo.ico',
                ),
            ]
        )
        mock_board_posts_response.assert_called_once_with(
            board_detail_info=mock_board_detail_info.return_value,
            posts=[mock_board_post.return_value, mock_board_post.return_value],
            has_previous=False,
            has_next=False,
            previous_page_number=None,
            current_page_number=1,
            next_page_number=None,
            last_page_number=1,
            page_range=[1],
        )

    def test_get_tagged_posts_nonexistent_board(self):
        # Given: 존재하지 않는 게시판
        board_url = 'nonexistent-board'

        # When: HTTP GET 요청
        response = self.client.get(
            reverse(
                self.view_name,
                kwargs={'tag_name': 'NoTagName'},
            )
        )

        # Then: HTTP 응답
        self.assertEqual(response.status_code, 404)
