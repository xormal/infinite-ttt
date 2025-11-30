"""Integration tests for the network server and client.

These tests start the server in a background thread, connect a client, send a
single move and verify that the client receives a board update containing that
move. The server is bound to an OS‑assigned free port to avoid conflicts.
"""

import socket
import threading
import time
from contextlib import closing

from src.network_server import TicTacToeServer
from src.network_client import TicTacToeClient


def _find_free_port() -> int:
    """Return an available TCP port on the localhost interface."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_server_receives_move_and_broadcasts(monkeypatch):
    port = _find_free_port()

    # Start server in a daemon thread
    server = TicTacToeServer(host="127.0.0.1", port=port)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    # Give the server a moment to start listening
    time.sleep(0.2)

    # Connect a client manually (skip the full client class to keep test simple)
    client_sock = socket.create_connection(("127.0.0.1", port))
    try:
        # Send a move "0,0"
        client_sock.sendall(b"0,0")
        # Receive the board payload (ends with double newline)
        data = b""
        while not data.endswith(b"\n\n"):
            chunk = client_sock.recv(1024)
            if not chunk:
                break
            data += chunk
        payload = data.decode().strip().splitlines()
        # Expect at least one line with the move we sent
        assert any(line.startswith("0,0,") for line in payload)
    finally:
        client_sock.close()
