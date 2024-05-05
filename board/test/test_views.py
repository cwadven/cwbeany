import json

from django.test import TestCase
from django.urls import reverse

from board.models import Board, BoardGroup
from board.views import get_boards_info_from_board_group


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
