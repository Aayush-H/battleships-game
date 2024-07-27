import random
#import database_manager
#from database_manager import DatabaseManager

class Ship:
    def __init__(self, size):
        self.size = size
        self.positions = []
        self.hits = 0

    def place(self, start_x, start_y, orientation):
        self.positions = []
        for i in range(self.size):
            if orientation == "horizontal":
                self.positions.append((start_x + i, start_y))
            else:
                self.positions.append((start_x, start_y + i))

    def is_sunk(self):
        return self.hits == self.size

class Board:
    def __init__(self, size=10):
        self.size = size
        self.grid = [[' ' for _ in range(size)] for _ in range(size)]
        self.ships = []

    def place_ship(self, ship):
        for x, y in ship.positions:
            if self.grid[x][y] != ' ':
                return False
        for x, y in ship.positions:
            self.grid[x][y] = 'S'
        self.ships.append(ship)
        return True

    def receive_attack(self, x, y):
        if self.grid[x][y] == 'S':
            self.grid[x][y] = 'X'
            for ship in self.ships:
                if (x, y) in ship.positions:
                    ship.hits += 1
                    return 'hit'
        elif self.grid[x][y] == ' ':
            self.grid[x][y] = 'O'
            return 'miss'
        else:
            return 'already attacked'

    def all_ships_sunk(self):
        return all(ship.is_sunk() for ship in self.ships)

    def __str__(self):
        return '\n'.join([' '.join(row) for row in self.grid])

    def is_ship_sunk(self, x, y):
        for ship in self.ships:
            if (x, y) in ship.positions:
                return ship.is_sunk()
        return False

class ComputerPlayer:
    def __init__(self, board_size,difficulty):
        from database_manager import DatabaseManager
        self.board_size = board_size
        self.difficulty = difficulty
        self.db_manager = DatabaseManager()

    def place_ships(self, ships):
        board = Board(self.board_size)
        predefined_board = self.db_manager.get_random_predefined_board(self.difficulty)
        if predefined_board:
            self.place_ships_from_coordinates(board, predefined_board)
        else:
            self.place_ships_randomly(board, ships)
        return board

    def place_ships_from_coordinates(self, board, coordinates):
        for ship_data in coordinates.split('|'):
            ship_type, coords = ship_data.split(':')
            ship_coords = [tuple(map(int, coord.split(','))) for coord in coords.split(';')]
            ship = Ship(len(ship_coords))
            ship.positions = ship_coords
            board.place_ship(ship)

    def place_ships_randomly(self, board, ships):
        # ... (existing random placement code)
        for ship in ships:
            placed = False
            while not placed:
                x = random.randint(0, self.board_size - 1)
                y = random.randint(0, self.board_size - 1)
                orientation = random.choice(["horizontal", "vertical"])

                new_ship = Ship(ship.size)
                new_ship.place(x, y, orientation)

                if all(0 <= px < self.board_size and 0 <= py < self.board_size for px, py in new_ship.positions):
                    placed = board.place_ship(new_ship)
        return board


    # def place_ships(self, ships):
    #     board = Board(self.board_size)
    #     for ship in ships:
    #         placed = False
    #         while not placed:
    #             x = random.randint(0, self.board_size - 1)
    #             y = random.randint(0, self.board_size - 1)
    #             orientation = random.choice(["horizontal", "vertical"])

    #             new_ship = Ship(ship.size)
    #             new_ship.place(x, y, orientation)

    #             if all(0 <= px < self.board_size and 0 <= py < self.board_size for px, py in new_ship.positions):
    #                 placed = board.place_ship(new_ship)
    #     return board

    def make_move(self, opponent_board):
        while True:
            x = random.randint(0, self.board_size - 1)
            y = random.randint(0, self.board_size - 1)
            if opponent_board.grid[x][y] in [' ', 'S']:
                return x, y
