import random
import sys
import threading
import queue

TIMEOUT = 60  # seconds allowed for each input

LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # columns
    (0, 4, 8), (2, 4, 6),              # diagonals
]


class InputTimeout(Exception):
    pass


_input_queue = queue.Queue()


def _stdin_reader():
    """Runs in the background and forwards every typed line to the queue."""
    while True:
        line = sys.stdin.readline()
        if line == "":          # stdin closed
            _input_queue.put(None)
            break
        _input_queue.put(line.rstrip("\n"))


threading.Thread(target=_stdin_reader, daemon=True).start()


def timed_input(prompt):
    print(prompt, end="", flush=True)
    try:
        line = _input_queue.get(timeout=TIMEOUT)
    except queue.Empty:
        raise InputTimeout
    if line is None:
        raise EOFError
    return line.strip()


# ---------- game logic ----------

def print_board(board):
    print()
    for r in range(3):
        cells = [board[3 * r + c] if board[3 * r + c] != " " else str(3 * r + c + 1)
                 for c in range(3)]
        print(" " + " | ".join(cells))
        if r < 2:
            print("---+---+---")
    print()


def winner(board):
    for a, b, c in LINES:
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a]
    return None


def board_full(board):
    return " " not in board


def completing_move(board, sign):
    """Return the free cell that completes a line already holding two `sign`s, else None."""
    for line in LINES:
        values = [board[i] for i in line]
        if values.count(sign) == 2 and values.count(" ") == 1:
            return line[values.index(" ")]
    return None


def computer_move(board, cpu_sign, player_sign):
    # 1. Win if the computer can complete a line
    move = completing_move(board, cpu_sign)
    if move is not None:
        return move
    # 2. Block a line where the player already has two symbols
    move = completing_move(board, player_sign)
    if move is not None:
        return move
    # 3. Otherwise, pick a random free cell
    return random.choice([i for i, v in enumerate(board) if v == " "])


# ---------- asking the player ----------

def ask_name():
    while True:
        name = timed_input("Enter your name: ")
        if name:
            return name
        print("Error: the name cannot be empty.")


def ask_sign():
    while True:
        s = timed_input("Choose your sign (X or 0): ").upper()
        if s == "X":
            return "X"
        if s in ("0", "O"):
            return "0"
        print("Error: invalid sign. Please type X or 0.")


def ask_move(board, name):
    while True:
        s = timed_input(f"{name}, choose a cell (1-9): ")
        if not s.isdigit():
            print("Error: please enter a number from 1 to 9.")
            continue
        n = int(s)
        if not 1 <= n <= 9:
            print("Error: the number must be between 1 and 9.")
            continue
        if board[n - 1] != " ":
            print("Error: that cell is already taken.")
            continue
        return n - 1


def ask_play_again():
    while True:
        s = timed_input("Do you want to play again? (y/n): ").lower()
        if s in ("y", "yes"):
            return True
        if s in ("n", "no"):
            return False
        print("Error: please answer y or n.")


# ---------- main ----------

def play_round(name, player_sign):
    cpu_sign = "0" if player_sign == "X" else "X"
    board = [" "] * 9
    turn = "X"  # X always starts
    print(f"\n{name} is {player_sign}, the computer is {cpu_sign}. X starts.")
    print_board(board)

    while True:
        if turn == player_sign:
            board[ask_move(board, name)] = player_sign
        else:
            move = computer_move(board, cpu_sign, player_sign)
            board[move] = cpu_sign
            print(f"The computer plays in cell {move + 1}.")
        print_board(board)

        w = winner(board)
        if w:
            print(f"{name} wins!" if w == player_sign else "The computer wins!")
            return
        if board_full(board):
            print("It's a draw!")
            return
        turn = "0" if turn == "X" else "X"


def main():
    print("=== Tic-Tac-Toe ===")
    print(f"(You have {TIMEOUT} seconds for each input.)\n")
    try:
        name = ask_name()
        while True:
            player_sign = ask_sign()
            play_round(name, player_sign)
            if not ask_play_again():
                print(f"Thanks for playing, {name}!")
                break
    except InputTimeout:
        print(f"\n\nTime out: no input received within {TIMEOUT} seconds. Game over.")
    except (EOFError, KeyboardInterrupt):
        print("\nGame interrupted.")


if __name__ == "__main__":
    main()
