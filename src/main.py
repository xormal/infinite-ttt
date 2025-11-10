#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Infinite Tic‑Tac‑Toe (3‑in‑a‑row) terminal game.

The game logic is kept pure where possible, allowing unit testing of core
functions without invoking curses. The main entry point launches the curses UI.
"""

import curses
import random
import time
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

# Project‑specific configuration and helper modules
from src.config import (
    DIFFICULTY,
    MOVE_TIMEOUT,
    ENABLE_POWERUPS,
    TWO_PLAYER_MODE,
    COLOR_PLAYER,
    COLOR_COMPUTER,
    COLOR_CURSOR,
)
from src.powerups import clear_random_line

# ---------------------------------------------------------------------------
# Constants & Directions
# ---------------------------------------------------------------------------
EMPTY = ' '
PLAYER = 'X'      # Human player symbol (or first player in two‑player mode)
COMPUTER = 'O'    # Computer player symbol (or second player)

# Directions: horizontal, vertical, and the two diagonals
DIRS: List[Tuple[int, int]] = [(1, 0), (0, 1), (1, 1), (1, -1)]


# ---------------------------------------------------------------------------
# Board utilities
# ---------------------------------------------------------------------------
def check_triples(board: Dict[Tuple[int, int], str], symbol: str) -> List[List[Tuple[int, int]]]:
    """Return a list of coordinate triples that form a line of *symbol*.

    Each triple is a list of three (x, y) positions. Overlapping triples are
    reported separately, matching the original game behaviour.
    """
    triples: List[List[Tuple[int, int]]] = []
    for (x, y), val in board.items():
        if val != symbol:
            continue
        for dx, dy in DIRS:
            line = [(x + i * dx, y + i * dy) for i in range(3)]
            if all(board.get(p) == symbol for p in line):
                triples.append(line)
    return triples


def remove_triples(board: Dict[Tuple[int, int], str], triples: List[List[Tuple[int, int]]]) -> None:
    """Remove all cells that belong to any triple in *triples*.
    The *board* dict is mutated in‑place.
    """
    for line in triples:
        for p in line:
            board.pop(p, None)


# ---------------------------------------------------------------------------
# Advanced AI for the computer player
# ---------------------------------------------------------------------------
def _winning_moves(board: Dict[Tuple[int, int], str], candidates: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Return candidate positions that would give *COMPUTER* an immediate triple."""
    wins: List[Tuple[int, int]] = []
    for pos in candidates:
        trial = dict(board)
        trial[pos] = COMPUTER
        if check_triples(trial, COMPUTER):
            wins.append(pos)
    return wins


def _threat_moves(board: Dict[Tuple[int, int], str], candidates: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Return positions where *PLAYER* could win on the next turn.

    The computer should block any of these cells.
    """
    threats: List[Tuple[int, int]] = []
    for pos in candidates:
        trial = dict(board)
        trial[pos] = PLAYER
        if check_triples(trial, PLAYER):
            threats.append(pos)
    return threats


def _heuristic_score(board: Dict[Tuple[int, int], str], pos: Tuple[int, int]) -> int:
    """Simple heuristic: count number of 2‑in‑a‑row lines that would include *pos*.

    The score helps prefer moves that create future opportunities for the
    computer. Only lines of exactly two *COMPUTER* symbols (including the new
    one) without any *PLAYER* symbols are counted.
    """
    score = 0
    # Simulate placing the computer symbol at *pos*
    trial = dict(board)
    trial[pos] = COMPUTER
    for dx, dy in DIRS:
        # Count symbols of COMPUTER in this direction (both forward and backward)
        count = 0
        # forward direction
        for step in range(1, 3):
            p = (pos[0] + step * dx, pos[1] + step * dy)
            if trial.get(p) == COMPUTER:
                count += 1
            elif trial.get(p) == PLAYER:
                count = -1  # blocked by opponent
                break
        # backward direction
        if count != -1:
            for step in range(1, 3):
                p = (pos[0] - step * dx, pos[1] - step * dy)
                if trial.get(p) == COMPUTER:
                    count += 1
                elif trial.get(p) == PLAYER:
                    count = -1
                    break
        if count > 0:
            # Two symbols (including the new one) is a promising line
            score += count
    return score


def computer_move(board: Dict[Tuple[int, int], str], cursor: Tuple[int, int], view_radius: int = 5) -> Optional[Tuple[int, int]]:
    """Choose the computer's next move.

    The algorithm prefers:
    1. A winning move (completing a triple).
    2. Blocking an immediate player win.
    3. A move that creates the most 2‑in‑a‑row opportunities.
    4. A random nearby free cell.

    *cursor* is the current player cursor; only cells within *view_radius*
    (Manhattan distance) are considered. If no cells are found, the function
    expands the search to the full board.
    """
    cx, cy = cursor
    # Gather free cells in the view radius
    candidates: List[Tuple[int, int]] = []
    for dx in range(-view_radius, view_radius + 1):
        for dy in range(-view_radius, view_radius + 1):
            pos = (cx + dx, cy + dy)
            if pos not in board:
                candidates.append(pos)
    # If nothing around the cursor, fall back to any empty cell adjacent to any occupied cell
    if not candidates:
        # Find all positions adjacent (Manhattan distance 1) to existing pieces
        adjacent: set[Tuple[int, int]] = set()
        for (x, y) in board.keys():
            for ax, ay in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                neighbor = (x + ax, y + ay)
                if neighbor not in board:
                    adjacent.add(neighbor)
        candidates = sorted(adjacent)
        if not candidates:
            return None
    else:
        # Ensure deterministic order for reproducibility
        candidates = sorted(candidates)

    # 1. Look for a winning move
    wins = _winning_moves(board, candidates)
    if wins:
        return wins[0]

    # 2. Block opponent's winning move
    threats = _threat_moves(board, candidates)
    if threats:
        return threats[0]

    # 3. Heuristic: pick move creating most 2‑in‑a‑row lines
    best_score = -1
    best_pos: Optional[Tuple[int, int]] = None
    for pos in candidates:
        score = _heuristic_score(board, pos)
        if score > best_score:
            best_score = score
            best_pos = pos
    if best_pos is not None and best_score > 0:
        return best_pos

    # 4. Fallback random move (deterministic fallback to first candidate)
    return candidates[0] if candidates else None


# ---------------------------------------------------------------------------
# Curses UI
# ---------------------------------------------------------------------------
def _init_colors() -> None:
    """Initialise curses colour pairs using values from :mod:`src.config`."""
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(COLOR_PLAYER, curses.COLOR_RED, -1)
    curses.init_pair(COLOR_COMPUTER, curses.COLOR_CYAN, -1)
    curses.init_pair(COLOR_CURSOR, curses.COLOR_WHITE, curses.COLOR_BLUE)


def draw(stdscr, board, cursor, offset, scores, move_history):
    """Render the board without flicker.

    Empty cells are shown as a period ``.``. The cell under the cursor is
    highlighted using reverse video.
    """
    stdscr.erase()
    h, w = stdscr.getmaxyx()
    for y in range(h - 2):
        for x in range(w - 2):
            gx = x + offset[0]
            gy = y + offset[1]
            ch = board.get((gx, gy), EMPTY)
            # Determine visual attributes based on cell content or cursor
            if (gx, gy) == cursor:
                stdscr.attron(curses.A_REVERSE | curses.color_pair(COLOR_CURSOR))
                stdscr.addch(y + 1, x + 1, ch if ch != EMPTY else '.')
                stdscr.attroff(curses.A_REVERSE | curses.color_pair(COLOR_CURSOR))
            elif ch == PLAYER:
                stdscr.attron(curses.color_pair(COLOR_PLAYER))
                stdscr.addch(y + 1, x + 1, ch)
                stdscr.attroff(curses.color_pair(COLOR_PLAYER))
            elif ch == COMPUTER:
                stdscr.attron(curses.color_pair(COLOR_COMPUTER))
                stdscr.addch(y + 1, x + 1, ch)
                stdscr.attroff(curses.color_pair(COLOR_COMPUTER))
            else:
                stdscr.addch(y + 1, x + 1, '.')
    stdscr.border()
    # Build a brief move history (last 5 moves) for the status line.
    recent = ', '.join([f"{sym}{pos}" for pos, sym in move_history[-5:]])
    stdscr.addstr(
        0,
        2,
        f' X: {scores[PLAYER]} O: {scores[COMPUTER]}  Hist: {recent}  (Q – quit) ',
    )
    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    # Initialise colour pairs for UI rendering.
    _init_colors()

    board: Dict[Tuple[int, int], str] = {}
    scores: defaultdict[str, int] = defaultdict(int)
    cursor: Tuple[int, int] = (0, 0)
    offset: Tuple[int, int] = (-10, -5)

    # History of moves – each entry is ``((x, y), symbol)``.
    move_history: List[Tuple[Tuple[int, int], str]] = []

    # Symbol whose turn it is (used for two‑player mode).
    current_symbol: str = PLAYER

    # Timestamp of the most recent move (human or computer).
    last_move_time: float = time.time()

    while True:
        draw(stdscr, board, cursor, offset, scores, move_history)

        key = stdscr.getch()
        move_made = False

        if key == -1:
            # No input – fall through to timer handling.
            pass
        elif key in (ord('q'), ord('Q')):
            break
        elif key == curses.KEY_UP:
            cursor = (cursor[0], cursor[1] - 1)
        elif key == curses.KEY_DOWN:
            cursor = (cursor[0], cursor[1] + 1)
        elif key == curses.KEY_LEFT:
            cursor = (cursor[0] - 1, cursor[1])
        elif key == curses.KEY_RIGHT:
            cursor = (cursor[0] + 1, cursor[1])
        elif key == ord(' '):
            if cursor not in board:
                # Human (or player) move using the active symbol.
                board[cursor] = current_symbol
                move_history.append((cursor, current_symbol))
                # Resolve any triples for the symbol just placed.
                while True:
                    triples = check_triples(board, current_symbol)
                    if not triples:
                        break
                    scores[current_symbol] += len(triples)
                    remove_triples(board, triples)
                move_made = True
                last_move_time = time.time()

                if not TWO_PLAYER_MODE:
                    # Computer response – use difficulty‑based view radius.
                    comp_pos = computer_move(board, cursor, view_radius=DIFFICULTY.value)
                    if comp_pos:
                        board[comp_pos] = COMPUTER
                        move_history.append((comp_pos, COMPUTER))
                        while True:
                            triples = check_triples(board, COMPUTER)
                            if not triples:
                                break
                            scores[COMPUTER] += len(triples)
                            remove_triples(board, triples)
                        move_made = True
                        last_move_time = time.time()
                else:
                    # Two‑player mode – switch turn to the opposite symbol.
                    current_symbol = PLAYER if current_symbol == COMPUTER else COMPUTER
        elif key == ord('p') and ENABLE_POWERUPS:
            # Power‑up: clear a random line on the board.
            clear_random_line(board)
            move_made = True
            last_move_time = time.time()

        # Automatic computer move after timeout (human‑vs‑computer only).
        if not move_made and not TWO_PLAYER_MODE and MOVE_TIMEOUT > 0:
            now = time.time()
            if now - last_move_time >= MOVE_TIMEOUT:
                comp_pos = computer_move(board, cursor, view_radius=DIFFICULTY.value)
                if comp_pos:
                    board[comp_pos] = COMPUTER
                    move_history.append((comp_pos, COMPUTER))
                    while True:
                        triples = check_triples(board, COMPUTER)
                        if not triples:
                            break
                        scores[COMPUTER] += len(triples)
                        remove_triples(board, triples)
                    last_move_time = now
                    move_made = True

        # Auto‑scroll to keep cursor visible
        h, w = stdscr.getmaxyx()
        cx, cy = cursor
        ox, oy = offset
        if cx - ox < 2:
            offset = (cx - 2, oy)
        elif cx - ox > w - 4:
            offset = (cx - (w - 4), oy)
        if cy - oy < 2:
            offset = (offset[0], cy - 2)
        elif cy - oy > h - 4:
            offset = (offset[0], cy - (h - 4))

        # Avoid busy‑loop when no move occurred – give CPU a brief pause.
        if not move_made:
            curses.napms(10)


if __name__ == '__main__':
    curses.wrapper(main)
