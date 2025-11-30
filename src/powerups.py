"""Power‑up utilities for Infinite Tic‑Tac‑Toe.

Provides a single power‑up that clears a random line (row or column) of a
configurable length from the board. The board is a ``dict`` mapping ``(x, y)``
coordinates to a single‑character symbol.
"""

from __future__ import annotations

import random
from typing import Dict, Tuple
from src.types import Board

# The board maps ``(x, y)`` coordinates to a single‑character symbol.

# ---------------------------------------------------------------------------
# Configurable range for random line generation – импортируем из конфигурации
from src.config import MIN_COORD, MAX_COORD
 
# Exported symbols for ``from src.powerups import *``
__all__ = [
    "clear_random_line",
    "MIN_COORD",
    "MAX_COORD",
    "Board",
]


def clear_random_line(board: Board, length: int = 5) -> None:
    """Remove a random horizontal or vertical line of *length* cells.

    The line is chosen uniformly from the set of possible positions that are
    centred around the origin ``(0, 0)``. Cells that are not present in the
    ``board`` are simply ignored – the function only deletes existing entries.

    Parameters
    ----------
    board:
        The mutable game board.
    length:
        Number of cells to clear in the chosen line. Must be an odd number so
        that the line can be symmetrically centred; the default (5) works well
        for typical gameplay.
    """
    if length % 2 == 0:
        raise ValueError("length must be odd to allow symmetric clearing")

    orientation = random.choice(["horizontal", "vertical"])
    half = length // 2

    if orientation == "horizontal":
        y = random.randint(MIN_COORD, MAX_COORD)
        for dx in range(-half, half + 1):
            board.pop((dx, y), None)
    else:  # vertical
        x = random.randint(MIN_COORD, MAX_COORD)
        for dy in range(-half, half + 1):
            board.pop((x, dy), None)
