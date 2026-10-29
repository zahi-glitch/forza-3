# Tic-Tac-Toe for 1 player

import random

# Functions: print_board, get_move, computer_move, check_winner_or_draw

def print_board(board):
    for row_cells in board:
        print("|".join(row_cells)) # prints whole row  with "|" as separator
        print("-" * 5)             # prints a line of dashes to separate rows

def get_move(board):
    while True:                    # ask input until valid
        # try / except: execute block and catch exceptions
        while True:                # ask row until valid
            try:
                row = int(input("Enter row (0-2): "))
            except ValueError:
                print("Invalid input! Please enter a whole number between 0 and 2.")
                continue
            if row not in range(3):
                print("Row must be between 0 and 2.")
                continue
            break

        while True:               # ask for column until valid
            try:
                col = int(input("Enter column (0-2): "))
            except ValueError:
                print("Invalid input! Please enter a whole number between 0 and 2.")
                continue
            if col not in range(3):
                print("Column must be between 0 and 2.")
                continue
            break

        # check chosen cell is free
        if board[row][col] != " ":
            print("Cell is already taken. Try again.")
        else:
            return row, col

def computer_move(board):
    # collect all free cells, then pick one at random
    free = [(r, c) for r in range(3) for c in range(3) if board[r][c] == " "]
    return random.choice(free)

def check_winner_or_draw(board):
    # create a list of all possible winning lines (rows, columns, diagonals)
    lines = [
        *board, # * unpacks the board into a single list of lines
        *[[board[row][col] for row in range(3)] for col in range(3)], # columns, outer loop picks fixed coordinate
        # diagonals
        [board[i][i] for i in range(3)],
        [board[i][2 - i] for i in range(3)],
    ]

    if any(line[0] == line[1] == line[2] != " " for line in lines):
        return "win"

    if all(cell != " " for row in board for cell in row):
        return "draw"

    return None


# Main

print("Let's play Tic Tac Toe. You are X, the computer is O.")   # CHANGED

board = [[" "] * 3 for _ in range(3)]   # list of lists
player = 1                              # player 1 (human) starts

for i in range(9):
    if player == 1:                      
        print("Your turn.")
    else:
        print("Computer's turn.")
    print_board(board)

    if player == 1:
        row, col = get_move(board)       # human
    else:
        row, col = computer_move(board)  # computer
        print(f"Computer plays row {row}, column {col}.")

    board[row][col] = "X" if player == 1 else "O"

    result = check_winner_or_draw(board)

    if result == "win":
        print_board(board)
        if player == 1:                 
            print("You win!")
        else:
            print("The computer wins!")
        break
    elif result == "draw":
        print_board(board)
        print("It's a draw!")
        break
    player = 2 if player == 1 else 1  # switch players
