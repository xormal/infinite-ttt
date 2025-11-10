#!/usr/bin/env python3
"""Entry point for the Infinite Tic‑Tac‑Toe game.

This thin wrapper imports the actual game implementation from ``src.main``
and starts it using ``curses.wrapper``. It exists to satisfy the
documentation reference to ``infinite_ttt.py`` and provides a convenient
executable for ``python -m infinite_ttt``.
"""

import curses
from src.main import main as game_main


def _run() -> None:
    """Run the game inside a curses session."""
    curses.wrapper(game_main)


if __name__ == "__main__":
    _run()

