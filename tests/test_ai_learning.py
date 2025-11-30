"""Тесты для модуля ``src.ai_learning``.

Проверяют базовую работу функций обучения: запись и чтение оценок ходов.
Тесты используют реальный файл ``ai_data.json`` в корне репозитория, но
очищают его после выполнения, чтобы не оставлять следов.
"""

import os
import json
from pathlib import Path

import pytest

from src.ai_learning import record_move, get_move_score, DATA_PATH


@pytest.fixture(autouse=True)
def clean_data_file():
    """Удалить файл ``ai_data.json`` до и после каждого теста.

    Это гарантирует, что тесты изолированы и не влияют друг на друга.
    """
    # Ensure a clean state before the test.
    if os.path.exists(DATA_PATH):
        os.remove(DATA_PATH)
    yield
    # Clean up after the test.
    if os.path.exists(DATA_PATH):
        os.remove(DATA_PATH)


def test_initial_score_is_zero():
    """Для неизвестной позиции ожидается нулевой счёт."""
    assert get_move_score((0, 0)) == 0


def test_record_move_updates_score():
    """Проверка корректного инкремента/декремента оценки.

    После успешного хода счёт должен увеличиться на 1, после неуспешного –
    уменьшиться на 1.
    """
    pos = (1, -2)
    # Первый успешный ход
    record_move(pos, True)
    assert get_move_score(pos) == 1
    # Неуспешный ход уменьшит счёт
    record_move(pos, False)
    assert get_move_score(pos) == 0


def test_data_file_is_json_and_persists():
    """После записи файл должен существовать и содержать корректный JSON."""
    pos = (3, 3)
    record_move(pos, True)
    assert Path(DATA_PATH).exists()
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    key = f"{pos[0]},{pos[1]}"
    assert data.get(key) == 1

