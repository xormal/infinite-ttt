"""Тесты для нового power‑up «дополнительный ход»."""

from src.powerups_extra import extra_turn, Board


def test_extra_turn_returns_true() -> None:
    # Пустая доска – тип Board, но функция не использует её.
    board: Board = {}
    assert extra_turn(board) is True

