#!/usr/bin/env sh

# Entry point for the Docker container. It simply runs the network server.
# The server reads ``SERVER_HOST`` and ``SERVER_PORT`` environment variables,
# allowing the container user to override the defaults.
exec python -m src.network_server "$@"
