# Simple development helper Makefile

PYTHON ?= python3
VENV_DIR ?= .venv
REQS ?= requirements.txt

.PHONY: install clean run docker-up docker-down server client precommit test lint docker-logs docker-shell

# -----------------------------------
# Install dependencies into a virtual environment.
# -----------------------------------
install:
	@echo "Creating virtual environment…"
	@$(PYTHON) -m venv $(VENV_DIR)
	@. $(VENV_DIR)/bin/activate && pip install --upgrade pip
	@. $(VENV_DIR)/bin/activate && pip install -r $(REQS)
	@echo "Installation complete. Activate with 'source $(VENV_DIR)/bin/activate'."

# -----------------------------------
# Run the game locally.
# -----------------------------------
run:
	@$(PYTHON) -m src.main

# -------------------------------------------------
# Pre‑commit hook installation
# -------------------------------------------------
precommit:
	@pre-commit install

# Run the TCP server (network multiplayer)
server:
	@$(PYTHON) -m src.network_server

# Run the TCP client (connect to the server)
client:
	@$(PYTHON) -m src.network_client

# -----------------------------------
# Build and start the Docker services.
# -----------------------------------
docker-up:
	docker-compose up --build

# -----------------------------------
# Stop Docker services and clean up.
# -----------------------------------
docker-down:
	docker-compose down

# -----------------------------------
# Clean up generated files.
# -----------------------------------
clean:
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@rm -rf $(VENV_DIR)
	# Additional Docker helpers
	docker-logs:
		@docker-compose logs -f

	docker-shell:
		@docker-compose exec network_server sh

# -------------------------------------------------------------------
# Testing and linting shortcuts
# -------------------------------------------------------------------

.PHONY: test lint

test:
	@$(PYTHON) -m pytest -q

lint:
	@flake8 src tests
	@black --check src tests
