"""Клиентская часть сетевой игры Infinite Tic‑Tac‑Toe.

Подключается к серверу, отправляет координаты ходов и отображает полученные
обновления доски в терминале. В текущей среде сетевой доступ ограничен, но
код остаётся полностью рабочим при запуске в обычной сети.
"""

from __future__ import annotations

import socket
import threading
import sys
from typing import Tuple


class TicTacToeClient:
    """TCP‑клиент для обмена ходами с сервером.

    Параметры
    ----------
    host: str
        Адрес сервера (по умолчанию ``127.0.0.1``).
    port: int
        Порт сервера (по умолчанию ``5555``).
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 5555) -> None:
        self.host: str = host
        self.port: int = port
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self) -> None:
        """Установить соединение и запустить потоки ввода/вывода."""
        self.sock.connect((self.host, self.port))
        threading.Thread(target=self._receive_loop, daemon=True).start()
        self._input_loop()

    def _receive_loop(self) -> None:
        """Читать обновления доски от сервера и выводить их в консоль."""
        buffer: str = ""
        while True:
            try:
                data: bytes = self.sock.recv(4096)
            except ConnectionResetError:
                print("Disconnected from server")
                break
            if not data:
                break
            buffer += data.decode()
            # Обновления разделяются двойным переводом строки.
            while "\n\n" in buffer:
                raw_board, buffer = buffer.split("\n\n", 1)
                self._render_board(raw_board)

    def _render_board(self, raw: str) -> None:
        """Преобразовать строковое представление доски в табличный вывод.

        Формат ``raw`` – строки ``x,y,sym``. Функция группирует клетки по ``y``
        и печатает строки от минимального до максимального ``y``.
        """
        cells: dict[Tuple[int, int], str] = {}
        for line in raw.splitlines():
            try:
                x_str, y_str, sym = line.split(',')
                x, y = int(x_str), int(y_str)
                cells[(x, y)] = sym
            except ValueError:
                continue
        if not cells:
            return
        min_x = min(x for x, _ in cells)
        max_x = max(x for x, _ in cells)
        min_y = min(y for _, y in cells)
        max_y = max(y for _, y in cells)
        for y in range(min_y, max_y + 1):
            row = []
            for x in range(min_x, max_x + 1):
                row.append(cells.get((x, y), '.'))
            print(''.join(row))
        print('-' * 20)

    def _input_loop(self) -> None:
        """Считывать координаты ходов из ``stdin`` и отправлять их серверу."""
        print("Enter moves as ``x y`` (e.g. ``0 0``). Type ``quit`` to exit.")
        for line in sys.stdin:
            line = line.strip()
            if line.lower() in {"quit", "exit", "q"}:
                break
            parts = line.split()
            if len(parts) != 2:
                print("Invalid input – provide two integers")
                continue
            try:
                x, y = int(parts[0]), int(parts[1])
            except ValueError:
                print("Coordinates must be integers")
                continue
            msg = f"{x},{y}".encode()
            try:
                self.sock.sendall(msg)
            except Exception:
                print("Failed to send move – connection may be closed")
                break
        self.sock.close()


if __name__ == "__main__":
    client = TicTacToeClient()
    client.start()

