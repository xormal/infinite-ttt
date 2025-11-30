"""Тесты для модуля ``src.powerups``.

Проверяют, что константы диапазона заданы корректно и что функция
``clear_random_line`` действительно удаляет клетки из доски.
"""

import random
from typing import Dict, Tuple

import pytest

from src.powerups import MIN_COORD, MAX_COORD, clear_random_line, Board


def test_constants_range():
    """MIN_COORD и MAX_COORD должны быть целыми и MIN < MAX."""
    assert isinstance(MIN_COORD, int)
    assert isinstance(MAX_COORD, int)
    assert MIN_COORD < MAX_COORD


def test_clear_random_line_removes_cells(monkeypatch):
    """Функция должна удалять ровно *length* ячеек, если они присутствуют.

    Для предсказуемости фиксируем выбор ориентации и координаты через
    ``monkeypatch``.
    """
    # Подготовим доску с известными координатами.
    board: Board = {
        (0, 0): "X",
        (1, 0): "O",
        (-1, 0): "X",
        (0, 1): "O",
        (0, -1): "X",
    }

    # Фиксируем ориентацию горизонтальной и координату y = 0.
    monkeypatch.setattr(random, "choice", lambda seq: "horizontal")
    monkeypatch.setattr(random, "randint", lambda a, b: 0)

    clear_random_line(board, length=3)

    # После очистки горизонтальная линия y=0 должна быть удалена полностью.
    assert (0, 0) not in board
    assert (1, 0) not in board
    assert (-1, 0) not in board
    # Вертикальные клетки должны остаться.
    assert (0, 1) in board
    assert (0, -1) in board

