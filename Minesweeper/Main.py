import numpy as np
import os
import sys
from collections import deque

def clear_console():
    # Check if the operating system is Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # Assume macOS or Linux for other cases
    else:
        _ = os.system('clear')

clear_console()
print("what size board would you like")
print("1:5x5, 2:10x10, 3:15x15, 4:20x20, 5:25x25")
Size = int(input("Please choose a num batween 1-5: "))
Main_board = np.tile(0, (Size*5,Size*5))
Revealed = np.zeros_like(Main_board, dtype=bool)
arraylength = np.arange(Size*5+1)

def BombLocations(S):
    density: float = 0.16
    if not (0 < density < 1):
        raise ValueError("density must be between 0 and 1 (exclusive)")

    rows = cols = S * 5
    total = rows * cols

    # Compute number of bombs proportional to area
    num_bombs = int(round(total * density))
    num_bombs = max(1, min(total - 1, num_bombs)) # keep at least 1 empty cell

    rng = np.random.default_rng()

    # Choose unique bomb positions without replacement
    bomb_flat_idxs = rng.choice(total, size=num_bombs, replace=False)

    board = np.zeros((rows, cols), dtype=int)
    board.flat[bomb_flat_idxs] = 1
    return board

def Board(board, bomb_value: int = 1, bomb_marker: int = -1):
    if board.ndim != 2:
        raise ValueError("board must be 2D")
    
    rows, cols = board.shape
    result = board.copy() 
    for r in range(rows):
        for c in range(cols):
            if board[r, c] == bomb_value:
                result[r, c] = bomb_marker
                continue

            neighbor_sum = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        neighbor_sum += 1 if board[nr, nc] == bomb_value else 0
            result[r, c] = neighbor_sum
    return result

Backboard = Board(BombLocations(Size))
    
def Check_bomb(locat):
    # Ensure we have plain row/col ints (avoid NumPy fancy indexing)
    if isinstance(locat, tuple):
        r, c = locat
    else:
        r, c = int(locat[0]), int(locat[1])

    rows, cols = Backboard.shape
    val = int(Backboard[r, c])

    if val == -1:
        Main_board[r, c] = -1
        Revealed[r, c] = True
        return False

    if val > 0:
        Main_board[r, c] = val
        Revealed[r, c] = True
        return True
    
    q = deque([(r, c)])
    visited = set()
    
    while q:
        cr, cc = q.popleft()
        if (cr, cc) in visited:
            continue
        visited.add((cr, cc))

        # Reveal the zero itself
        Main_board[cr, cc] = 0
        Revealed[cr, cc] = True  

        # Explore 8 neighbors
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = cr + dr, cc + dc
                if not (0 <= nr < rows and 0 <= nc < cols):
                    continue

                nval = int(Backboard[nr, nc])
                if nval == -1:
                    continue # never reveal bombs
                if nval == 0:
                    # enqueue further zeros for flood
                    if (nr, nc) not in visited:
                        q.append((nr, nc))
                elif nval > 0:
                    Main_board[nr, nc] = nval
                    Revealed[nr, nc] = True

    return True

def show_board():
    rows, cols = Main_board.shape

    # Pick a fixed cell width large enough for headers and cell contents
    cell_w = max(2, len(str(rows)), len(str(cols)))

    # Header (column numbers 1..cols)
    header_nums = " ".join(f"{i:>{cell_w}}" for i in range(1, cols + 1))
    print(" " * (cell_w + 1) + header_nums)

    # Body
    for r in range(rows):
        row_cells = []
        for c in range(cols):
            if not Revealed[r, c]:
                s = "."
            else:
                v = Main_board[r, c]
                s = "X" if v == -1 else str(int(v))
            row_cells.append(s.rjust(cell_w))
        print(f"{r+1:>{cell_w}} " + " ".join(row_cells))
    print()

def main():
    rows, cols = Main_board.shape
    while True:
        clear_console()
        show_board()
        print("Would you like to guss or place a flag")
        try:
            flag = int(input("1 for guss and 2 for flag: "))
            if flag == 1:
                is_flag = False
            elif flag == 2:
                is_flag = True
            else:
                print("please choose eather 1 or 2")
                main()
        except ValueError:
            print("Please enter whole numbers.")
            continue
        clear_console()
        show_board()

        try:
            col_in = int(input(f"Please choose the Column (1..{cols}): ").strip())
            row_in = int(input(f"Please choose the Row (1..{rows}): ").strip())
        except ValueError:
            print("Please enter whole numbers.")
            continue
        
        # Convert from 1-based to 0-based
        r = row_in - 1
        c = col_in - 1

        # Bounds check
        if not (0 <= r < rows and 0 <= c < cols):
            print(f"Out of bounds. Row must be 1..{rows}, Column must be 1..{cols}.")
            continue

        print(f"Would you like to choose Row {row_in}, Column {col_in}? ")
        yn = input("Y/N ").strip().lower()
        location = np.array([r,c], dtype=int)
        if yn.startswith('y'):
            safe = Check_bomb(location)
            if is_flag:
                clear_console()
                show_board()
                print("You Lost")
                Reset = str(input("Reset Y/N"))
                if Reset.startswith('y'):
                    os.execl(sys.executable, sys.executable, *sys.argv)
            else:
                if safe:
                    main()
                else:
                    clear_console()
                    show_board()
                    print("You Lost")
                    Reset = str(input("Reset Y/N"))
                    if Reset.startswith('y'):
                        os.execl(sys.executable, sys.executable, *sys.argv)
        if yn.startswith('n'):
            main()

main()