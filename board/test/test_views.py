import json

from django.test import (
    Client,
    TestCase,
)
from django.urls import reverse

from accounts.models import User
from board.models import (
    Board,
    BoardGroup, Post, Tag,
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

    def test_get_board_posts_with_search(self):
        # Given: 검색어 'Post 1'
        search = 'Post 1'

        # When: HTTP GET 요청
        response = self.client.get(
            reverse(
                self.view_name,
                kwargs={'board_url': 'test-board'}),
            {'search': search},
        )

        # Then: HTTP 응답
        self.assertEqual(response.status_code, 200)
        # And: 응답 데이터 검증
        self.assertContains(response, 'Post 1')
        self.assertNotContains(response, 'Post 2')
        # And: has_previous 페이지가 하나 뿐이어서 False
        self.assertEqual(response.context['has_previous'], False)
        # And: has_next 페이지가 하나 뿐이어서 False
        self.assertEqual(response.context['has_next'], False)
        # And: 이전 페이지 정보
        self.assertEqual(response.context['previous_page_number'], None)
        # And: 현재 페이지 정보
        self.assertEqual(response.context['current_page_number'], 1)
        # And: 다음 페이지 정보
        self.assertEqual(response.context['next_page_number'], None)
        # And: 마지막 페이지 정보
        self.assertEqual(response.context['last_page_number'], 1)
        # And: 페이지 범위
        self.assertEqual(
            set(response.context['page_range']),
            {1}
        )
        # And: 유효한 HTML 파일
        self.assertTemplateUsed(response, 'board/board_detail.html')

    def test_get_board_posts_pagination_first_page(self):
        # Given: 15개의 게시물 생성
        for i in range(15):
            Post.objects.create(
                title=f'Post {i + 3}',
                body=f'Body {i + 3}',
                board=self.board,
                author=self.user,
            )

        # When: 첫 번째 페이지 요청
        response = self.client.get(
            reverse(
                self.view_name,
                kwargs={'board_url': 'test-board'}),
            {'page': 1}
        )

        # Then: HTTP 응답
        self.assertEqual(response.status_code, 200)
        # And: 최신순으로 조회하기 때문에 1페이지에 5 ~ 15까지의 게시물이 나와야 함
        self.assertContains(response, 'Post 12')
        self.assertNotContains(response, 'Post 3')
        # And: 첫번째 페이지에 현재 있어서 이전 페이지 없음
        self.assertEqual(response.context['has_previous'], False)
        # And: 페이지가 2개 있어서 다음 페이지 있음
        self.assertEqual(response.context['has_next'], True)
        # And: 이전 페이지 정보
        self.assertEqual(response.context['previous_page_number'], None)
        # And: 현재 페이지 정보
        self.assertEqual(response.context['current_page_number'], 1)
        # And: 다음 페이지 정보
        self.assertEqual(response.context['next_page_number'], 2)
        # And: 마지막 페이지 정보
        self.assertEqual(response.context['last_page_number'], 2)
        # And: 페이지 범위
        self.assertEqual(
            set(response.context['page_range']),
            {1, 2}
        )
        # And: 유효한 HTML 파일
        self.assertTemplateUsed(response, 'board/board_detail.html')

    def test_get_board_posts_no_search(self):
        # Given: 검색어 없음
        # When: HTTP GET 요청
        response = self.client.get(reverse(self.view_name, kwargs={'board_url': 'test-board'}))

        # Then: HTTP 응답
        self.assertEqual(response.status_code, 200)
        # And: 응답 데이터 검증
        self.assertContains(response, 'Post 1')
        self.assertContains(response, 'Post 2')
        # And: has_previous 페이지가 하나 뿐이어서 False
        self.assertEqual(response.context['has_previous'], False)
        # And: has_next 페이지가 하나 뿐이어서 False
        self.assertEqual(response.context['has_next'], False)
        # And: 이전 페이지 정보
        self.assertEqual(response.context['previous_page_number'], None)
        # And: 현재 페이지 정보
        self.assertEqual(response.context['current_page_number'], 1)
        # And: 다음 페이지 정보
        self.assertEqual(response.context['next_page_number'], None)
        # And: 마지막 페이지 정보
        self.assertEqual(response.context['last_page_number'], 1)
        # And: 페이지 범위
        self.assertEqual(
            set(response.context['page_range']),
            {1}
        )
        # And: 유효한 HTML 파일
        self.assertTemplateUsed(response, 'board/board_detail.html')

    def test_get_board_posts_nonexistent_board(self):
        # Given: 존재하지 않는 게시판
        board_url = 'nonexistent-board'

        # When: HTTP GET 요청
        response = self.client.get(reverse(self.view_name, kwargs={'board_url': board_url}))

        # Then: HTTP 응답
        self.assertEqual(response.status_code, 404)

    def test_get_board_posts_with_multiple_pages(self):
        # Given: 15개의 게시물 생성
        for i in range(15):
            Post.objects.create(
                title=f'Post {i + 3}',
                body=f'Body {i + 3}',
                board=self.board,
                author=self.user,
            )

        # When
        response = self.client.get(reverse(self.view_name, kwargs={'board_url': 'test-board'}), {'page': 2})

        # Then: HTTP 응답
        self.assertEqual(response.status_code, 200)
        # And: 최신순으로 조회하기 때문에 2페이지에 4 ~ 1 까지의 게시물이 나와야 함
        self.assertContains(response, 'Post 3')
        self.assertNotContains(response, 'Post 12')
        # And: has_previous 가 True 여서 이전 페이지로 이동 가능해야 함
        self.assertEqual(response.context['has_previous'], True)
        # And: 마지막 페이지여서 다음 페이지로 이동 불가능해야 함
        self.assertEqual(response.context['has_next'], False)
        # And: 이전 페이지 정보
        self.assertEqual(response.context['previous_page_number'], 1)
        # And: 현재 페이지 정보
        self.assertEqual(response.context['current_page_number'], 2)
        # And: 다음 페이지 정보
        self.assertEqual(response.context['next_page_number'], None)
        # And: 마지막 페이지 정보
        self.assertEqual(response.context['last_page_number'], 2)
        # And: 페이지 범위
        self.assertEqual(
            set(response.context['page_range']),
            {1, 2}
        )
        # And: 유효한 HTML 파일
        self.assertTemplateUsed(response, 'board/board_detail.html')


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

    def test_get_tagged_posts_with_search(self):
        # Given: 검색어 'Post'
        search = 'Post'

        # When: HTTP GET 요청
        response = self.client.get(
            reverse(
                self.view_name,
                kwargs={'tag_name': self.tag1.tag_name}),
            {'search': search},
        )

        # Then: HTTP 응답
        self.assertEqual(response.status_code, 200)
        # And: 응답 데이터 검증
        self.assertContains(response, 'Post 1')
        self.assertNotContains(response, 'Post 2')
        # And: has_previous 페이지가 하나 뿐이어서 False
        self.assertEqual(response.context['has_previous'], False)
        # And: has_next 페이지가 하나 뿐이어서 False
        self.assertEqual(response.context['has_next'], False)
        # And: 이전 페이지 정보
        self.assertEqual(response.context['previous_page_number'], None)
        # And: 현재 페이지 정보
        self.assertEqual(response.context['current_page_number'], 1)
        # And: 다음 페이지 정보
        self.assertEqual(response.context['next_page_number'], None)
        # And: 마지막 페이지 정보
        self.assertEqual(response.context['last_page_number'], 1)
        # And: 페이지 범위
        self.assertEqual(
            set(response.context['page_range']),
            {1}
        )
        # And: 유효한 HTML 파일
        self.assertTemplateUsed(response, 'board/tagged_board_detail.html')

    def test_get_tagged_posts_pagination_first_page(self):
        # Given: 15개의 게시물 생성
        for i in range(15):
            post = Post.objects.create(
                title=f'Post {i + 3}',
                body=f'Body {i + 3}',
                board=self.board,
                author=self.user,
            )
            post.tag_set.add(self.tag1)
        # And: Post 2 에도 tag1 추가
        self.post2.tag_set.add(self.tag1)

        # When: 첫 번째 페이지 요청
        response = self.client.get(
            reverse(
                self.view_name,
                kwargs={'tag_name': self.tag1.tag_name}),
            {'page': 1}
        )

        # Then: HTTP 응답
        self.assertEqual(response.status_code, 200)
        # And: 최신순으로 조회하기 때문에 1페이지에 5 ~ 15까지의 게시물이 나와야 함
        self.assertContains(response, 'Post 12')
        self.assertNotContains(response, 'Post 3')
        # And: 첫번째 페이지에 현재 있어서 이전 페이지 없음
        self.assertEqual(response.context['has_previous'], False)
        # And: 페이지가 2개 있어서 다음 페이지 있음
        self.assertEqual(response.context['has_next'], True)
        # And: 이전 페이지 정보
        self.assertEqual(response.context['previous_page_number'], None)
        # And: 현재 페이지 정보
        self.assertEqual(response.context['current_page_number'], 1)
        # And: 다음 페이지 정보
        self.assertEqual(response.context['next_page_number'], 2)
        # And: 마지막 페이지 정보
        self.assertEqual(response.context['last_page_number'], 2)
        # And: 페이지 범위
        self.assertEqual(
            set(response.context['page_range']),
            {1, 2}
        )
        # And: 유효한 HTML 파일
        self.assertTemplateUsed(response, 'board/tagged_board_detail.html')

    def test_get_tagged_posts_no_search(self):
        # Given: 검색어 없음
        # When: HTTP GET 요청
        response = self.client.get(
            reverse(
                self.view_name,
                kwargs={'tag_name': self.tag1.tag_name},
            )
        )

        # Then: HTTP 응답
        self.assertEqual(response.status_code, 200)
        # And: 응답 데이터 검증
        self.assertContains(response, 'Post 1')
        self.assertNotContains(response, 'Post 2')
        # And: has_previous 페이지가 하나 뿐이어서 False
        self.assertEqual(response.context['has_previous'], False)
        # And: has_next 페이지가 하나 뿐이어서 False
        self.assertEqual(response.context['has_next'], False)
        # And: 이전 페이지 정보
        self.assertEqual(response.context['previous_page_number'], None)
        # And: 현재 페이지 정보
        self.assertEqual(response.context['current_page_number'], 1)
        # And: 다음 페이지 정보
        self.assertEqual(response.context['next_page_number'], None)
        # And: 마지막 페이지 정보
        self.assertEqual(response.context['last_page_number'], 1)
        # And: 페이지 범위
        self.assertEqual(
            set(response.context['page_range']),
            {1}
        )
        # And: 유효한 HTML 파일
        self.assertTemplateUsed(response, 'board/tagged_board_detail.html')

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

    def test_get_tagged_posts_with_multiple_pages(self):
        # Given: 15개의 게시물 생성
        for i in range(15):
            post = Post.objects.create(
                title=f'Post {i + 3}',
                body=f'Body {i + 3}',
                board=self.board,
                author=self.user,
            )
            post.tag_set.add(self.tag1)
        # And: Post 2 에도 tag1 추가
        self.post2.tag_set.add(self.tag1)

        # When
        response = self.client.get(
            reverse(
                self.view_name,
                kwargs={'tag_name': self.tag1.tag_name},
            ),
            {
                'page': 2
            }
        )

        # Then: HTTP 응답
        self.assertEqual(response.status_code, 200)
        # And: 최신순으로 조회하기 때문에 2페이지에 4 ~ 1 까지의 게시물이 나와야 함
        self.assertContains(response, 'Post 3')
        self.assertNotContains(response, 'Post 12')
        # And: has_previous 가 True 여서 이전 페이지로 이동 가능해야 함
        self.assertEqual(response.context['has_previous'], True)
        # And: 마지막 페이지여서 다음 페이지로 이동 불가능해야 함
        self.assertEqual(response.context['has_next'], False)
        # And: 이전 페이지 정보
        self.assertEqual(response.context['previous_page_number'], 1)
        # And: 현재 페이지 정보
        self.assertEqual(response.context['current_page_number'], 2)
        # And: 다음 페이지 정보
        self.assertEqual(response.context['next_page_number'], None)
        # And: 마지막 페이지 정보
        self.assertEqual(response.context['last_page_number'], 2)
        # And: 페이지 범위
        self.assertEqual(
            set(response.context['page_range']),
            {1, 2}
        )
        # And: 유효한 HTML 파일
        self.assertTemplateUsed(response, 'board/tagged_board_detail.html')
