"""Skeleton client for connecting to ``src.network_server``.

The client reads user input from the terminal (coordinates) and sends them to
the server. It also receives board updates from the server and prints a simple
textual representation. This module is provided for completeness – the
environment's network access is restricted, so the code cannot be exercised
here, but it can be used locally.
"""

from __future__ import annotations

import socket
import threading
import sys
from typing import Tuple


class TicTacToeClient:
    """Connect to a Tic‑Tac‑Toe server and exchange moves.

    Parameters
    ----------
    host:
        Server hostname or IP address.
    port:
        Server listening port.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 5555) -> None:
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self) -> None:
        self.sock.connect((self.host, self.port))
        threading.Thread(target=self._receive_loop, daemon=True).start()
        self._input_loop()

    def _receive_loop(self) -> None:
        """Continuously read board updates from the server."""
        buffer = ""
        while True:
            try:
                data = self.sock.recv(4096)
            except ConnectionResetError:
                print("Disconnected from server")
                break
            if not data:
                break
            buffer += data.decode()
            # Board updates are separated by a double newline.
            while "\n\n" in buffer:
                raw_board, buffer = buffer.split("\n\n", 1)
                self._render_board(raw_board)

    def _render_board(self, raw: str) -> None:
        """Print a simple human‑readable board representation.

        The ``raw`` string consists of lines ``x,y,sym``. This method groups the
        cells by their ``y`` coordinate and prints rows from top to bottom.
        """
        cells = {}
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
        """Read ``x y`` coordinates from stdin and send them to the server."""
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
