"""Серверная часть сетевой игры Infinite Tic‑Tac‑Toe.

Принимает простые текстовые сообщения ``x,y`` от клиентов, обновляет общую
доску и рассылает её всем подключённым клиентам. Протокол минимален и
предназначен только для демонстрации; в продакшене потребуются проверки и
аутентификация.
"""

from __future__ import annotations

import os
import socket
import threading
from typing import Dict, Tuple, List
from src.logger import get_logger

logger = get_logger(__name__)

# Тип доски – словарь координат → символ.
Board = Dict[Tuple[int, int], str]


class TicTacToeServer:
    """Простой TCP‑сервер для многопользовательской игры.

    Параметры ``host`` и ``port`` могут быть заданы явно или через переменные
    окружения ``SERVER_HOST`` и ``SERVER_PORT``. По умолчанию сервер слушает
    ``0.0.0.0:5555``.
    """

    def __init__(self, host: str | None = None, port: int | None = None) -> None:
        self.host: str = host or os.getenv("SERVER_HOST", "0.0.0.0")
        self.port: int = int(port or os.getenv("SERVER_PORT", "5555"))
        self.board: Board = {}
        self.clients: List[socket.socket] = []
        self.lock = threading.Lock()

    def start(self) -> None:
        """Создать слушающий сокет и принимать подключения в бесконечном цикле.

        Добавлена обработка KeyboardInterrupt и гарантированное закрытие сокета.
        """
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((self.host, self.port))
        srv.listen()
        logger.info(f"Tic‑Tac‑Toe server listening on {self.host}:{self.port}")
        try:
            while True:
                client, addr = srv.accept()
                logger.info(f"Client connected from {addr}")
                with self.lock:
                    self.clients.append(client)
                threading.Thread(target=self._handle_client, args=(client,), daemon=True).start()
        except KeyboardInterrupt:
            logger.info("Server shutdown requested via KeyboardInterrupt")
        finally:
            srv.close()

    def _handle_client(self, conn: socket.socket) -> None:
        """Обрабатывать сообщения от одного клиента.

        Ожидается формат ``x,y``. На каждый полученный ход сервер помещает
        символ ``O`` (компьютер) в соответствующую ячейку и рассылает обновлённую
        доску всем клиентам.
        """
        with conn:
            while True:
                try:
                    data = conn.recv(1024)
                except ConnectionResetError:
                    logger.warning("Client connection reset")
                    break
                except Exception as e:
                    logger.error(f"Unexpected error in client handler: {e}")
                    break
                if not data:
                    break
                try:
                    x_str, y_str = data.decode().strip().split(',')
                    x, y = int(x_str), int(y_str)
                except Exception:
                    # Игнорировать некорректные сообщения.
                    continue
                with self.lock:
                    self.board[(x, y)] = "O"
                    self._broadcast_board()

    def _broadcast_board(self) -> None:
        """Отправить всем клиентам текстовое представление текущей доски.

        Формат: строки ``x,y,sym`` разделённые переводом строки, завершаются
        двойным переводом строки, чтобы клиент мог разбить поток.
        """
        payload_lines = [f"{x},{y},{sym}" for (x, y), sym in self.board.items()]
        payload = "\n".join(payload_lines) + "\n\n"
        for client in self.clients[:]:
            try:
                client.sendall(payload.encode())
            except Exception:
                # Удаляем недоступные клиенты.
                with self.lock:
                    if client in self.clients:
                        self.clients.remove(client)


if __name__ == "__main__":
    server = TicTacToeServer()
    server.start()
