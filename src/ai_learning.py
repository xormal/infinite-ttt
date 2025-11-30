"""Simple self‑learning utilities for the computer AI.

The implementation stores a lightweight score for each board position in a
JSON file ``ai_data.json`` located at the repository root.  Positive scores
indicate that moves to the position have historically contributed to a triple
for the computer, while negative scores indicate the opposite.

Only the *high* difficulty (``Difficulty.HARD``) uses these scores – they are
added to the base heuristic in :func:`src.main.computer_move`.
"""

import json
import os
from typing import Tuple, Dict

# Path to the persistent data file (one level above ``src``)
DATA_PATH = os.path.join(os.path.dirname(__file__), os.pardir, "ai_data.json")


def _load_data() -> Dict[str, int]:
    """Load the JSON data file, returning an empty dict if it does not exist.

    Returns
    -------
    Dict[str, int]
        Mapping from ``"x,y"`` coordinate strings to integer scores.
    """
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def _save_data(data: Dict[str, int]) -> None:
    """Write the data back to ``ai_data.json`` atomically.

    Parameters
    ----------
    data:
        Mapping of coordinate keys to their learned scores.
    """
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f)


def _key(pos: Tuple[int, int]) -> str:
    """Convert a coordinate tuple to a string key for JSON storage.

    The JSON file stores positions as ``"x,y"`` strings, so this helper
    provides a single source of truth for that conversion.
    """
    return f"{pos[0]},{pos[1]}"


def record_move(pos: Tuple[int, int], success: bool) -> None:
    """Update the learning data for a computer move.

    * ``pos`` – board coordinate of the move.
    * ``success`` – ``True`` if the move resulted in at least one triple for
      the computer (i.e., a positive outcome), otherwise ``False``.
    """
    data = _load_data()
    k = _key(pos)
    data.setdefault(k, 0)
    data[k] += 1 if success else -1
    _save_data(data)


def get_move_score(pos: Tuple[int, int]) -> int:
    """Return the learned score for *pos* (default ``0`` if unknown)."""
    return _load_data().get(_key(pos), 0)

# Public API of this module
__all__ = ["record_move", "get_move_score"]
