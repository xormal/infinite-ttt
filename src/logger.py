"""Простейший логгер для проекта.

Внутренний модуль, который настраивает стандартный `logging` и предоставляет
функцию `get_logger(name)` для получения именованного логгера. По умолчанию
уровень – INFO, а вывод идёт в stdout. При необходимости проект может расширить
конфигурацию (например, добавить файловый хендлер).
"""

import logging
import sys


def _configure_root() -> None:
    """Настраивает корневой логгер один раз.

    Формат: ``%(asctime)s %(levelname)s %(name)s – %(message)s``.
    """
    root = logging.getLogger()
    if root.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s – %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)
    root.setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Возвращает готовый к использованию логгер.

    Вызывает конфигурацию корневого логгера при первом обращении.
    """
    _configure_root()
    return logging.getLogger(name)

