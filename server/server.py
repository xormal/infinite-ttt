"""Network server for Infinite Tic‑Tac‑Toe.

Runs a TCP server that coordinates a shared game board among multiple
clients. The server maintains the authoritative board state, resolves triples
(`three‑in‑a‑row`), updates scores, and broadcasts the board after each valid
move.

Clients (e.g., :mod:`src.network_client`) send coordinates as ``"x,y"``
ASCII lines and receive a payload of ``"x,y,symbol"`` lines terminated by a blank
line.
"""

from __future__ import annotations

import socket
import threading
from collections import defaultdict
from typing import Dict, Tuple, List

# Core game logic – imported without the UI components.
from src.main import (
    PLAYER,
    COMPUTER,
    check_triples,
    remove_triples,
)

Board = Dict[Tuple[int, int], str]
ScoreMap = defaultdict[str, int]

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 5555


class TicTacToeServer:
    """Multi‑client server for the infinite board game.

    The first two connections are assigned the symbols ``X`` (human) and ``O``
    (computer) and alternate turns. Additional connections are treated as
    spectators – they receive board updates but cannot place moves.
    """

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
        self.host = host
        self.port = port
        self.board: Board = {}
        self.scores: ScoreMap = defaultdict(int)
        self.clients: List[socket.socket] = []
        # Map each client socket to the symbol it controls (empty for spectators).
        self.client_symbols: Dict[socket.socket, str] = {}
        self.lock = threading.Lock()
        self.turn_index = 0  # Index into active player list for turn order.

    # ---------------------------------------------------------------------
    # Server lifecycle
    # ---------------------------------------------------------------------
    def start(self) -> None:
        """Listen for incoming connections and spawn a thread per client."""
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
                # Assign symbols to the first two clients.
                if len([s for s in self.client_symbols.values() if s]) == 0:
                    self.client_symbols[client] = PLAYER
                elif len([s for s in self.client_symbols.values() if s]) == 1:
                    self.client_symbols[client] = COMPUTER
                else:
                    self.client_symbols[client] = ""  # spectator
            threading.Thread(target=self._handle_client, args=(client,), daemon=True).start()

    # ---------------------------------------------------------------------
    # Client handling
    # ---------------------------------------------------------------------
    def _handle_client(self, conn: socket.socket) -> None:
        """Process incoming move messages from *conn*.

        Expected payload: ``b"x,y"`` where *x* and *y* are signed integers.
        The server validates turn order, updates the board, and then broadcasts
        the full board state to all clients.
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
                    x_str, y_str = data.decode().strip().split(",")
                    x, y = int(x_str), int(y_str)
                except Exception:
                    # Malformed message – ignore.
                    continue
                symbol = self.client_symbols.get(conn, "")
                if not symbol:
                    # Spectator – ignore move.
                    continue
                # Enforce turn order.
                active = [s for s in self.client_symbols.values() if s]
                if symbol != active[self.turn_index % len(active)]:
                    continue
                self._process_move((x, y), symbol)
                # Advance turn after a successful move.
                self.turn_index = (self.turn_index + 1) % len(active)
                self._broadcast_board()
        # Cleanup on disconnect.
        with self.lock:
            if conn in self.clients:
                self.clients.remove(conn)
            if conn in self.client_symbols:
                del self.client_symbols[conn]
            # Reset turn index if needed.
            if self.turn_index >= len([s for s in self.client_symbols.values() if s]):
                self.turn_index = 0

    # ---------------------------------------------------------------------
    # Game logic
    # ---------------------------------------------------------------------
    def _process_move(self, pos: Tuple[int, int], symbol: str) -> None:
        """Place *symbol* at *pos* and resolve any resulting triples.

        Mutates ``self.board`` and ``self.scores``. If the cell is already
        occupied the move is ignored.
        """
        with self.lock:
            if pos in self.board:
                return
            self.board[pos] = symbol
            # Resolve triples for the player that just moved.
            while True:
                triples = check_triples(self.board, symbol)
                if not triples:
                    break
                self.scores[symbol] += len(triples)
                remove_triples(self.board, triples)

    # ---------------------------------------------------------------------
    # Broadcasting
    # ---------------------------------------------------------------------
    def _broadcast_board(self) -> None:
        """Send the current board to all connected clients.

        Payload format: one line per occupied cell – ``"x,y,symbol"`` –
        terminated by a blank line. Clients can parse this stream to render the
        board.
        """
        with self.lock:
            lines = [f"{x},{y},{sym}" for (x, y), sym in self.board.items()]
            payload = "\n".join(lines) + "\n\n"
            dead: List[socket.socket] = []
            for client in self.clients:
                try:
                    client.sendall(payload.encode())
                except Exception:
                    dead.append(client)
            for d in dead:
                self.clients.remove(d)
                if d in self.client_symbols:
                    del self.client_symbols[d]


if __name__ == "__main__":
    server = TicTacToeServer()
    server.start()

