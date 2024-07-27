# initialize_db.py

from predefined_boards import PREDEFINED_BOARDS
from database_manager import DatabaseManager

def board_to_coordinates(board):
    coordinates = []
    ships = {'C': 5, 'B': 4, 'D': 3, 'S': 3, 'P': 2}
    for ship, size in ships.items():
        ship_coords = []
        for i in range(10):
            for j in range(10):
                if board[i][j] == ship:
                    ship_coords.append((i, j))
        if ship_coords:
            coordinates.append(f"{size}:{';'.join([f'{x},{y}' for x, y in ship_coords])}")
    return '|'.join(coordinates)

def initialize_predefined_boards():
    db_manager = DatabaseManager()

    # Check if boards are already initialized
    db_manager.cursor.execute("SELECT COUNT(*) FROM predefined_boards")
    if db_manager.cursor.fetchone()[0] > 0:
        print("Predefined boards are already initialized.")
        return

    for difficulty, boards in PREDEFINED_BOARDS.items():
        for board in boards:
            ship_coordinates = board_to_coordinates(board)
            db_manager.add_predefined_board(difficulty.lower(), ship_coordinates)

    print("Predefined boards have been initialized in the database.")

if __name__ == "__main__":
    initialize_predefined_boards()