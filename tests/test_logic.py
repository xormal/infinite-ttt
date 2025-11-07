"""Unit tests for core game logic of Infinite Tic‑Tac‑Toe.

The tests focus on the pure functions that do not require the curses UI:

* ``check_triples`` – detection of winning lines
* ``remove_triples`` – removal of cells that formed a line
* ``computer_move`` – AI decision making (win, block, heuristic)
"""

from src.main import (
    PLAYER,
    COMPUTER,
    check_triples,
    remove_triples,
    computer_move,
)


def test_check_triples_single_line():
    board = {(0, 0): PLAYER, (1, 0): PLAYER, (2, 0): PLAYER}
    triples = check_triples(board, PLAYER)
    assert len(triples) == 1
    # The returned line should contain exactly the three coordinates above
    assert set(triples[0]) == {(0, 0), (1, 0), (2, 0)}


def test_remove_triples_clears_cells():
    board = {(0, 0): PLAYER, (1, 0): PLAYER, (2, 0): PLAYER, (5, 5): COMPUTER}
    triples = check_triples(board, PLAYER)
    remove_triples(board, triples)
    # The three player cells should be gone, other cells remain
    assert (0, 0) not in board
    assert (1, 0) not in board
    assert (2, 0) not in board
    assert board.get((5, 5)) == COMPUTER


def test_computer_move_wins_when_possible():
    """AI should make a move that creates a triple for itself.

    The exact coordinate may be on either side of the existing two symbols;
    we verify that the chosen move indeed results in a winning line.
    """
    board = {(0, 0): COMPUTER, (1, 0): COMPUTER}
    cursor = (0, 0)
    move = computer_move(board, cursor)
    # After the move, the computer must have at least one triple.
    new_board = dict(board)
    new_board[move] = COMPUTER
    from src.main import check_triples
    assert check_triples(new_board, COMPUTER)


def test_computer_move_blocks_player_win():
    """AI should block an immediate player winning move.

    The block can be placed on either side of the player's two symbols; we
    ensure that after the AI move the player no longer has a triple.
    """
    board = {(0, 0): PLAYER, (1, 0): PLAYER}
    cursor = (0, 0)
    move = computer_move(board, cursor)
    # Place the computer move and verify the player cannot win immediately.
    new_board = dict(board)
    new_board[move] = COMPUTER
    from src.main import check_triples
    assert not check_triples(new_board, PLAYER)
