from django.test import (
    RequestFactory,
    TestCase,
)

from board.dtos.request_dtos import BoardPostsRequest


class BoardPostsRequestTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_of_method_with_search(self):
        # Given: search 파라미터가 있는 GET 요청
        request = self.factory.get(
            '/some-url',
            {'search': 'test search'},
        )

        # When: BoardPostsRequest 객체 생성
        board_posts_request = BoardPostsRequest.of(request)

        # Then: search 파라미터가 정상적으로 설정되었는지 확인
        self.assertEqual(
            board_posts_request.search,
            'test search'
        )

    def test_of_method_without_search(self):
        # Given: search 파라미터가 없는 GET 요청
        request = self.factory.get('/some-url')

        # When: BoardPostsRequest 객체 생성
        board_posts_request = BoardPostsRequest.of(request)

        # Then: search 파라미터가 None으로 설정되었는지 확인
        self.assertEqual(
            board_posts_request.search,
            None
        )
