"""Файл настроек проекта «Бесконечные крестики‑нолики».

Все параметры задаются здесь, чтобы их можно было менять в одном месте.
"""

from enum import Enum


class Difficulty(Enum):
    """Определяет радиус поиска для ИИ.

    * EASY – 2 клетки от курсора
    * MEDIUM – 5 клеток (по умолчанию)
    * HARD – 8 клеток
    """

    EASY = 2
    MEDIUM = 5
    HARD = 8

# Текущий уровень сложности
DIFFICULTY: Difficulty = Difficulty.MEDIUM

# Таймер хода (секунды). 0 – отключён.
MOVE_TIMEOUT: int = 5

# Флаги включения дополнительных возможностей
ENABLE_POWERUPS: bool = False
TWO_PLAYER_MODE: bool = False

# Цветовые индексы для curses (используются в init_pair)
COLOR_PLAYER: int = 1
COLOR_COMPUTER: int = 2
COLOR_CURSOR: int = 3
# Диапазон координат, используемый в power‑up "очистка линии".
MIN_COORD: int = -10
MAX_COORD: int = 10
