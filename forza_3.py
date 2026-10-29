# Tic-Tac-Toe for 2 players

# Functions: print_board, get_move, check_winner_or_draw

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

print("Let's play Tic Tac Toe. Player 1 is X and Player 2 is O.")

board = [[" "] * 3 for _ in range(3)]   # list of  lists
player = 1                              # player 1 starts

for i in range(9):
    print(f"Player {player}'s turn.")
    print_board(board)
    row, col = get_move(board)


    board[row][col] = "X" if player == 1 else "O"


    result = check_winner_or_draw(board)


    if result == "win":
        print_board(board)
        print(f"Player {player} wins!")
        break
    elif result == "draw":
        print_board(board)
        print("It's a draw!")
        break
    player = 2 if player == 1 else 1  # switch players
