"""Power‑up utilities for Infinite Tic‑Tac‑Toe.

Provides a single power‑up that clears a random line (row or column) of a
configurable length from the board. The board is a ``dict`` mapping ``(x, y)``
coordinates to a single‑character symbol.
"""

from __future__ import annotations

import random
from typing import Dict, Tuple

# The board maps ``(x, y)`` coordinates to a single‑character symbol.
Board = Dict[Tuple[int, int], str]

# ---------------------------------------------------------------------------
# Configurable range for random line generation
# ---------------------------------------------------------------------------
# These constants define the inclusive range of coordinates from which the
# random line centre is chosen. Adjusting them changes the area of effect for
# the power‑up without touching the algorithm.
MIN_COORD: int = -10
MAX_COORD: int = 10


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

