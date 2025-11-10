"""Configuration module for Infinite Tic‑Tac‑Toe.

Centralised settings that control game behaviour. Values can be tweaked by
editing this file – the rest of the code imports them from :mod:`src.config`.
"""

from enum import Enum


class Difficulty(Enum):
    """AI difficulty levels – each maps to a view radius.

    The *view radius* limits the area around the cursor that the AI scans for
    candidate moves. A larger radius gives the AI a broader perspective and
    therefore stronger play.
    """

    EASY = 2
    MEDIUM = 5
    HARD = 8


# ---------------------------------------------------------------------------
# Game options – adjust to enable/disable features.
# ---------------------------------------------------------------------------

# Current AI difficulty. ``Difficulty.MEDIUM`` provides a balanced experience.
DIFFICULTY = Difficulty.MEDIUM

# Timeout (seconds) for a human move. ``0`` disables the timer.
MOVE_TIMEOUT = 5  # seconds; set to 0 to turn off automatic computer move

# Enable special power‑up actions (e.g., clear a random row/column).
ENABLE_POWERUPS = True

# Two‑player (human‑vs‑human) mode. When ``True`` the computer does not take a
# turn; the players alternate using the same keys.
TWO_PLAYER_MODE = False

# ---------------------------------------------------------------------------
# UI settings – colour pairs for curses UI. The actual colour initialisation
# happens in ``src.main``; these constants are only identifiers.
# ---------------------------------------------------------------------------

COLOR_PLAYER = 1   # ``X`` – red by default
COLOR_COMPUTER = 2  # ``O`` – cyan by default
COLOR_CURSOR = 3   # cursor highlight – white on blue background

