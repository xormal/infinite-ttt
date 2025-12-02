# Infinite Tic‑Tac‑Toe

## About the project
This is a text‑based implementation of **Infinite Tic‑Tac‑Toe**, a variant of the
classic “tic‑tac‑toe” game where the board has no fixed size. The goal is to
create a line of three identical symbols (X or O) in any direction – horizontal,
vertical or diagonal. When such a line appears, the cells are removed and the
player who formed the line receives a point. The game continues until the user
quits.

## History
* **1970s** – The concept of an “infinite” board first appeared in Soviet
  chess magazines as a logical puzzle.
* **1990s** – Early implementations in BASIC and C used dynamically growing
  arrays to represent the board.
* **2020s** – Several Python versions emerged, including this one, which relies
  only on the standard library and supports both single‑player (human vs simple
  AI) and networked multiplayer via a TCP server.

## Running the game
### Prerequisites
* Python 3.8+ (standard library only).
* A terminal that supports `curses` (on Windows you may need the `windows‑curses`
  package, installed automatically by `make install`).

### Install dependencies
```bash
make install   # creates .venv and installs from requirements.txt
```

### Start the game in the terminal
```bash
make run       # equivalent to: python -m src.main
```
Or run it directly without Make:
```bash
python -m src.main
```

### Networked play
1. **Start the server** (listens on `0.0.0.0:5555` by default):
   ```bash
   make server   # or: python -m server.server
   ```
2. **Start a client** (connects to `127.0.0.1:5555` by default):
   ```bash
   make client   # or: python -m src.network_client
   ```
   To change host/port edit the constants at the top of
   `src/network_client.py`.

## Controls
* **Arrow keys** – move the cursor.
* **Space** – place your symbol (`X`).
* **Q** – quit the game.
* **p** – activate a random power‑up (clears a random line). Available only if
  `ENABLE_POWERUPS = True` in `src/config.py`.
* In single‑player mode, after `MOVE_TIMEOUT` seconds of inactivity the AI
  makes a move (default 5 seconds).

## Game rules
1. Players alternate placing their symbol on an empty cell.
2. When a **triple** of identical symbols appears, those cells are removed and
   the player who formed the triple gains one point.
3. The board truly is infinite – coordinates keep their values after removals.
4. The game ends when the player presses `Q`. Scores are displayed and the
   winner is announced.

## Configuration
All settings live in `src/config.py`:
* `DIFFICULTY` – AI level (`EASY`, `MEDIUM`, `HARD`). Determines the search
  radius for the computer.
* `MOVE_TIMEOUT` – seconds of inactivity before the AI moves automatically.
* `ENABLE_POWERUPS` – enable/disable the `p` power‑up.
* `TWO_PLAYER_MODE` – two‑human‑player mode without AI.
* Color indices (`COLOR_PLAYER`, `COLOR_COMPUTER`, `COLOR_CURSOR`) are used by
  the curses UI.

## Tests & linting
```bash
make test      # runs pytest
make lint      # flake8 + black --check
```

## Docker
```bash
docker compose up --build   # builds the image and starts the server
```
The container forwards port **5555** (`5555:5555`). Override host/port with the
environment variables `SERVER_HOST` and `SERVER_PORT` when running the image.

## Contributing
* All communication (issues, PRs, comments) should be in **Russian** as per the
  repository guidelines.
* Follow the coding style from `AGENTS.md` (black formatting, snake_case for
  functions/variables, PascalCase for classes, etc.).
* When changing behaviour, add or update tests in the `tests/` directory.

---
**Enjoy the game!**

