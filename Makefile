# Simple development helper Makefile

PYTHON ?= python3
VENV_DIR ?= .venv
REQS ?= requirements.txt

.PHONY: install clean run docker-up docker-down

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

