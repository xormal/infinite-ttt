#!/usr/bin/env bash

# Simple wrapper to launch Infinite Tic‑Tac‑Toe using the module entry point.
# The script respects the project's virtual‑environment workflow.

set -euo pipefail

# Activate a virtual environment if present (optional)
if [[ -f ".venv/bin/activate" ]]; then
    # shellcheck source=/dev/null
    source ".venv/bin/activate"
fi

python -m src.main "$@"

