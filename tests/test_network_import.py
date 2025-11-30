"""Smoke tests that ensure network modules can be imported and instantiated.

Full network communication cannot be exercised in the sandbox (network is
restricted), but we can verify that the classes initialise correctly and that
type signatures are as expected.
"""

import pytest

from src.network_server import TicTacToeServer
from src.network_client import TicTacToeClient


def test_server_initialisation():
    server = TicTacToeServer(host="127.0.0.1", port=0)  # port 0 lets OS pick a free port
    # Ensure default attributes are set correctly.
    assert server.host == "127.0.0.1"
    assert isinstance(server.port, int)
    assert server.board == {}
    assert server.clients == []


def test_client_initialisation():
    client = TicTacToeClient(host="localhost", port=5555)
    assert client.host == "localhost"
    assert client.port == 5555
    # The socket is not yet connected; ensure it is a socket instance.
    assert client.sock.fileno() != -1
