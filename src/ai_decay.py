"""Модуль для затухания обучающих данных ИИ.

При каждом запуске игры накопленные оценки ИИ слегка уменьшаются, что
позволяет «забывать» старый опыт и адаптироваться к новым стратегиям.
"""

from .ai_learning import _load_data, _save_data

# Коэффициент затухания (0 < factor <= 1). При значении 0.9 оценки уменьшаются
# на 10 % каждый запуск.
DECAY_FACTOR: float = 0.9


def decay_learning_data() -> None:
    """Применить затухание к накопленным оценкам ИИ.

    Каждая оценка умножается на ``DECAY_FACTOR`` и округляется до целого.
    Оценки, ставшие нулём, удаляются из файла.
    """
    data = _load_data()
    for key in list(data.keys()):
        new_val = int(data[key] * DECAY_FACTOR)
        if new_val == 0:
            del data[key]
        else:
            data[key] = new_val
    _save_data(data)
