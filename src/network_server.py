"""Skeleton TCP server for multiplayer Infinite Tic‑Tac‑Toe.

The server receives plain‑text ``x,y`` coordinate messages from a client and
applies them to the shared game board. It broadcasts the updated board back to
all connected clients. This implementation does **not** perform any network I/O
in this repository's test environment (network access is restricted), but the
code illustrates how the feature could be wired up.
"""

from __future__ import annotations

import socket
import threading
from typing import Dict, Tuple, List

# Re‑use the board type from ``src.main`` for consistency.
Board = Dict[Tuple[int, int], str]


class TicTacToeServer:
    """Simple multi‑client server.

    Clients send moves as ``"x,y"`` (e.g. ``"3,-2"``). The server updates the board
    and forwards the new board state to all clients. No authentication or
    sophisticated protocol handling is provided – this is a minimal example.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 5555) -> None:
        self.host = host
        self.port = port
        self.board: Board = {}
        self.clients: List[socket.socket] = []
        self.lock = threading.Lock()

    def start(self) -> None:
        """Create listening socket and spawn a thread per client connection."""
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((self.host, self.port))
        srv.listen()
        print(f"Tic‑Tac‑Toe server listening on {self.host}:{self.port}")
        while True:
            client, addr = srv.accept()
            print(f"Client connected from {addr}")
            with self.lock:
                self.clients.append(client)
            threading.Thread(target=self._handle_client, args=(client,), daemon=True).start()

    def _handle_client(self, conn: socket.socket) -> None:
        """Receive moves from *conn* and broadcast updated board.

        Expected message format: ``"x,y"`` (ASCII digits, optional leading ``-``).
        """
        with conn:
            while True:
                try:
                    data = conn.recv(1024)
                except ConnectionResetError:
                    break
                if not data:
                    break
                try:
                    x_str, y_str = data.decode().strip().split(',')
                    x, y = int(x_str), int(y_str)
                except Exception:
                    # Invalid message – ignore.
                    continue
                with self.lock:
                    # For simplicity, always place the computer symbol.
                    self.board[(x, y)] = "O"
                    self._broadcast_board()

    def _broadcast_board(self) -> None:
        """Send a simple text representation of the board to all clients.

        The format is a series of ``"x,y,symbol"`` lines terminated by a blank
        line. Clients can parse this to reconstruct the state.
        """
        payload_lines = [f"{x},{y},{sym}" for (x, y), sym in self.board.items()]
        payload = "\n".join(payload_lines) + "\n\n"
        for client in self.clients:
            try:
                client.sendall(payload.encode())
            except Exception:
                # Remove dead client
                with self.lock:
                    if client in self.clients:
                        self.clients.remove(client)


if __name__ == "__main__":
    server = TicTacToeServer()
    server.start()

