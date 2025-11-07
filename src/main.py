#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Infinite Tic‑Tac‑Toe (3‑in‑a‑row) terminal game.

The game logic is kept pure where possible, allowing unit testing of core
functions without invoking curses. The main entry point launches the curses UI.
"""

import curses
import random
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

# ---------------------------------------------------------------------------
# Constants & Directions
# ---------------------------------------------------------------------------
EMPTY = ' '
PLAYER = 'X'      # Human player symbol
COMPUTER = 'O'    # Computer player symbol

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
def draw(stdscr, board, cursor, offset, scores):
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
            if (gx, gy) == cursor:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addch(y + 1, x + 1, ch if ch != EMPTY else '.')
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addch(y + 1, x + 1, ch if ch != EMPTY else '.')
    stdscr.border()
    stdscr.addstr(0, 2, f'  X: {scores[PLAYER]}  O: {scores[COMPUTER]}  (Q – quit)  ')
    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    board: Dict[Tuple[int, int], str] = {}
    scores: defaultdict[str, int] = defaultdict(int)
    cursor: Tuple[int, int] = (0, 0)
    offset: Tuple[int, int] = (-10, -5)

    while True:
        draw(stdscr, board, cursor, offset, scores)

        key = stdscr.getch()
        if key == -1:
            # Avoid busy‑loop when no input is available
            curses.napms(10)
            continue
        if key in (ord('q'), ord('Q')):
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
                # Human move
                board[cursor] = PLAYER
                # Resolve player triples
                while True:
                    triples = check_triples(board, PLAYER)
                    if not triples:
                        break
                    scores[PLAYER] += len(triples)
                    remove_triples(board, triples)

                # Computer move
                comp_pos = computer_move(board, cursor)
                if comp_pos:
                    board[comp_pos] = COMPUTER
                    while True:
                        triples = check_triples(board, COMPUTER)
                        if not triples:
                            break
                        scores[COMPUTER] += len(triples)
                        remove_triples(board, triples)

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


if __name__ == '__main__':
    curses.wrapper(main)

