from django.test import TestCase

from board.models import BoardGroup, Board
from board.services import get_boards_by_board_group_id


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
