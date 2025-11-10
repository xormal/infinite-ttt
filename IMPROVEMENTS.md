# Улучшения игрового процесса «Бесконечные крестики‑нолики»

В этом документе перечислены идеи, которые могут сделать игру более интересной,
разнообразной и удобной для игроков. Для каждой группы улучшений приведён
краткий обзор и пример кода, который иллюстрирует, как реализовать данную
функцию.

---

## 1. Сложность ИИ

### 1.1. Уровни сложности

Добавьте перечисление уровней и параметр `view_radius`, меняющий диапазон
поиска ходов. Пример:

```python
from enum import Enum


class Difficulty(Enum):
    EASY = 2
    MEDIUM = 5
    HARD = 8


def computer_move(board, cursor, difficulty=Difficulty.MEDIUM):
    """Выбирает ход ИИ, учитывая уровень сложности.

    * `difficulty` контролирует `view_radius`, то есть насколько далеко от
      курсора ищутся свободные клетки.
    """
    radius = difficulty.value
    return _computer_move_impl(board, cursor, view_radius=radius)
```

### 1.2. Минимакс с альфа‑бета‑отсечением (Hard)

Для «Hard»‑уровня можно использовать рекурсивный поиск, ограничивая глубину
чтобы не замедлять игру:

```python
def minimax(board, depth, maximizing, alpha=-float('inf'), beta=float('inf')):
    if depth == 0 or _is_terminal(board):
        return _evaluate(board)

    if maximizing:
        max_eval = -float('inf')
        for move in _available_moves(board):
            new_board = board.copy()
            new_board[move] = COMPUTER
            eval_ = minimax(new_board, depth - 1, False, alpha, beta)
            max_eval = max(max_eval, eval_)
            alpha = max(alpha, eval_)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in _available_moves(board):
            new_board = board.copy()
            new_board[move] = PLAYER
            eval_ = minimax(new_board, depth - 1, True, alpha, beta)
            min_eval = min(min_eval, eval_)
            beta = min(beta, eval_)
            if beta <= alpha:
                break
        return min_eval
```

## 2. Новые режимы игры

### 2.1. Два игрока (локальный)

Переименуйте символы и добавьте переменную `current_player`:

```python
CURRENT = PLAYER  # меняется на COMPUTER после каждого хода

def toggle_player():
    global CURRENT
    CURRENT = PLAYER if CURRENT == COMPUTER else COMPUTER

# В обработчике пробела ставим CURRENT, затем переключаем
if key == ord(' '):
    if cursor not in board:
        board[cursor] = CURRENT
        # проверка и удаление троек как обычно
        toggle_player()
```

### 2.2. Сетевая игра (TCP)

Создайте простой сервер‑клиент, пересылающий координаты ходов:

```python
# server.py
import socket
import threading
from src.main import board, process_move

HOST, PORT = '0.0.0.0', 5555
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen()

def handle(conn):
    while True:
        data = conn.recv(1024)
        if not data:
            break
        x, y = map(int, data.decode().split(','))
        process_move((x, y))
    conn.close()

while True:
    client, _ = sock.accept()
    threading.Thread(target=handle, args=(client,)).start()
```

## 3. Элементы геймплея

### 3.1. Пауэр‑ап «удалить случайный ряд»

```python
import random

def powerup_clear_random_row(board, length=5):
    # выбираем случайную вертикаль/горизонталь и удаляем клетки
    orientation = random.choice(['h', 'v'])
    if orientation == 'h':
        y = random.randint(-10, 10)
        for x in range(-length // 2, length // 2 + 1):
            board.pop((x, y), None)
    else:
        x = random.randint(-10, 10)
        for y in range(-length // 2, length // 2 + 1):
            board.pop((x, y), None)
```

### 3.2. Таймер хода

```python
import time

MOVE_TIMEOUT = 5  # секунд
last_move_time = time.time()

# внутри игрового цикла
if time.time() - last_move_time > MOVE_TIMEOUT:
    # автоматический переход хода компьютеру
    comp_pos = computer_move(board, cursor)
    if comp_pos:
        board[comp_pos] = COMPUTER
    last_move_time = time.time()
```

## 4. UI/UX улучшения

### 4.1. Цвета и подсказки

```python
def init_colors():
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)   # X
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)  # O
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)  # курсор

# При отрисовке используем pair
if (gx, gy) == cursor:
    stdscr.attron(curses.color_pair(3) | curses.A_REVERSE)
```

### 4.2. История ходов

```python
move_history: List[Tuple[Tuple[int, int], str]] = []

def record_move(pos, symbol):
    move_history.append((pos, symbol))

# При каждом новом ходу:
record_move(cursor, PLAYER)
```

## 5. Конфигурация и настройки

Создайте файл `src/config.py` со всеми параметрами, а в `src/main.py` импортируйте
их. Пример:

```python
# src/config.py
DIFFICULTY = 'MEDIUM'
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 24
```

В `src/main.py`:

```python
from src.config import DIFFICULTY
# использовать DIFFICULTY при инициализации ИИ
```

---

Эти предложения можно реализовать поэтапно: начать с уровней ИИ, добавить
мультиплеерный режим, а затем интегрировать улучшения UI и новые гейм‑механики.
Каждый блок кода снабжён минимумом контекста, чтобы его было легко вставить
в существующий проект.

