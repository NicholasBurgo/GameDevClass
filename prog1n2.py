import random

def main():
    ply = 1
    player = {"1": 0, "2": 0}
    b = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]

    print("Choose game mode:")
    print("1. Human vs Human")
    print("2. Human vs Computer")
    mode = int(input("Enter choice: "))

    while True:
        print("To play type (Top|Mid|Bottom) followed by (Left|Mid|Right)")
        if ply == 1:
            if mode == 1:
                move = input("Player one make a move: ")
            else:
                move = input("Player one make a move: ")
        else:
            if mode == 1:
                move = input("Player two make a move: ")
            else:
                print("Computer's turn")
                move = get_computer_move(b)

        # Convert move to coordinates
        row, col = convert_move(move)

        # Make move
        if b[row][col] == 0:
            b[row][col] = ply
        else:
            print("Invalid move! That space is already taken.")
            continue

        # Board drawing logic
        for i in range(3):
            if i == 0:
                print("-------------")
            for j in range(3):
                x = ""
                if b[i][j] == 0:
                    x = " "
                elif b[i][j] == 1:
                    x = "X"
                else:
                    x = "O"
                print(f" {x} ", end="")
                if j != 2:
                    print("|", end="")
            print()
            if i != 2:
                print("-------------")

        # Call winner function
        winner = check_winner(b)

        if winner:
            if winner == 1:
                print("Player 1 wins!")
            elif winner == 2:
                print("Player 2 wins!")
            else:
                print("Cat game!")
            break

        # Switch players
        ply = 2 if ply == 1 else 1

def convert_move(move):
    """Convert text move to row, col coordinates"""
    move = move.lower().strip()
    row = -1
    col = -1

    # Handle row
    if "top" in move:
        row = 0
    elif "middle" in move:
        row = 1
    elif "bottom" in move:
        row = 2

    # Handle column
    if "left" in move:
        col = 0
    elif "mid" in move:
        col = 1
    elif "right" in move:
        col = 2

    return row, col

def check_winner(b):
    # Check rows
    for i in range(3):
        if b[i][0] == b[i][1] == b[i][2] != 0:
            return b[i][0]
    # Column check
    for j in range(3):
        if b[0][j] == b[1][j] == b[2][j] != 0:
            return b[0][j]
    # Check diagonals
    if b[0][0] == b[1][1] == b[2][2] != 0:
        return b[0][0]
    if b[0][2] == b[1][1] == b[2][0] != 0:
        return b[1][1]

    # Check for draw
    if all(b[i][j] != 0 for i in range(3) for j in range(3)):
        return 3  # Draw
    return 0  # No winner

def get_winning_move(b, player):
    """Find winning move for player"""
    # Check rows
    for i in range(3):
        row = b[i]
        if row.count(player) == 2 and 0 in row:
            return (i, row.index(0))

    # Check columns
    for j in range(3):
        col = [b[i][j] for i in range(3)]
        if col.count(player) == 2 and 0 in col:
            return (col.index(0), j)

    # Check diagonals
    diag = [b[i][i] for i in range(3)]
    if diag.count(player) == 2 and 0 in diag:
        idx = diag.index(0)
        return (idx, idx)

    anti_diag = [b[i][2 - i] for i in range(3)]
    if anti_diag.count(player) == 2 and 0 in anti_diag:
        idx = anti_diag.index(0)
        return (idx, 2 - idx)
    return None

def get_computer_move(b):
    """Get computer move with strategy"""
    # Try to win
    win_move = get_winning_move(b, 2)
    if win_move:
        return convert_to_text(win_move[0], win_move[1])

    # Try to block
    block_move = get_winning_move(b, 1)
    if block_move:
        return convert_to_text(block_move[0], block_move[1])

    # Random move
    empty = [(i, j) for i in range(3) for j in range(3) if b[i][j] == 0]
    if empty:
        move = random.choice(empty)
        return convert_to_text(move[0], move[1])
    return "mid middle"

def convert_to_text(row, col):
    """Convert coordinates to text move"""
    row_text = ["top", "mid", "bottom"][row]
    col_text = ["left", "mid", "right"][col]
    return f"{row_text} {col_text}"

if __name__ == "__main__":
    main()