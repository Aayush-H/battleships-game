import sqlite3
from game_components import Board,Ship


class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('battleships.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        #self.initialize_predefined_boards()

    def create_tables(self):
        # Create tables for levels, game progress, move history, etc.
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS levels (
                id INTEGER PRIMARY KEY,
                name TEXT,
                board_layout TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_progress (
                id INTEGER PRIMARY KEY,
                level_id INTEGER,
                player_board TEXT,
                computer_board TEXT,
                current_turn INTEGER
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS move_history (
                id INTEGER PRIMARY KEY,
                game_id INTEGER,
                player TEXT,
                x INTEGER,
                y INTEGER,
                result TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                date_created DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            score INTEGER,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            total_ships_sunk INTEGER DEFAULT 0,
            total_moves INTEGER DEFAULT 0,
            games_played INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_statistics (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                turns INTEGER,
                hits INTEGER,
                misses INTEGER,
                ships_sunk INTEGER,
                time_taken REAL,
                date_played DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                board_size INTEGER DEFAULT 10,
                ship_configuration TEXT DEFAULT '5,4,3,3,2',
                difficulty TEXT DEFAULT 'medium',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS predefined_boards (
            id INTEGER PRIMARY KEY,
            difficulty TEXT,
            ship_coordinates TEXT
        )
        ''')

        self.conn.commit()

    def add_user(self, username, password, email):
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (username, password, email)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user(self, username, password):
        self.cursor.execute(
            "SELECT id, username, email FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        return self.cursor.fetchone()

    def add_level(self, name, board_layout):
        self.cursor.execute("INSERT INTO levels (name, board_layout) VALUES (?, ?)", (name, board_layout))
        self.conn.commit()

    def initialize_default_levels(self):
        self.cursor.execute("SELECT COUNT(*) FROM levels")
        if self.cursor.fetchone()[0] == 0:
            default_levels = [
                ("Easy", "Default easy layout"),
                ("Medium", "Default medium layout"),
                ("Hard", "Default hard layout")
            ]
            self.cursor.executemany("INSERT INTO levels (name, board_layout) VALUES (?, ?)", default_levels)
            self.conn.commit()

    def get_levels(self):
        self.cursor.execute("SELECT id, name FROM levels")
        return self.cursor.fetchall()

    def get_user_preferences(self, user_id):
        self.cursor.execute('''
            SELECT board_size, ship_configuration, difficulty
            FROM user_preferences
            WHERE user_id = ?
        ''', (user_id,))
        result = self.cursor.fetchone()
        if result:
            return {
                'board_size': result[0],
                'ship_configuration': result[1],
                'difficulty': result[2]
            }
        return {
            'board_size': 10,
            'ship_configuration': '5,4,3,3,2',
            'difficulty': 'medium'
        }

    def set_user_preferences(self, user_id, board_size, ship_configuration, difficulty):
        self.cursor.execute('''
            INSERT OR REPLACE INTO user_preferences
            (user_id, board_size, ship_configuration, difficulty)
            VALUES (?, ?, ?, ?)
        ''', (user_id, board_size, ship_configuration, difficulty))
        self.conn.commit()

    def add_game_statistics(self, user_id, turns, hits, misses, ships_sunk, time_taken):
        self.cursor.execute('''
            INSERT INTO game_statistics (user_id, turns, hits, misses, ships_sunk, time_taken)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, turns, hits, misses, ships_sunk, time_taken))
        self.conn.commit()

    def get_user_statistics(self, user_id):
        self.cursor.execute('''
            SELECT
                COUNT(*) as games_played,
                AVG(hits * 100.0 / (hits + misses)) as avg_accuracy,
                AVG(time_taken) as avg_time,
                SUM(ships_sunk) as total_ships_sunk,
                MIN(time_taken) as fastest_game
            FROM game_statistics
            WHERE user_id = ?
        ''', (user_id,))
        return self.cursor.fetchone()

    def add_predefined_board(self, difficulty, ship_coordinates):
        self.cursor.execute(
            "INSERT INTO predefined_boards (difficulty, ship_coordinates) VALUES (?, ?)",
            (difficulty, ship_coordinates)
        )
        self.conn.commit()

    def get_random_predefined_board(self, difficulty):
        self.cursor.execute(
            "SELECT ship_coordinates FROM predefined_boards WHERE difficulty = ? ORDER BY RANDOM() LIMIT 1",
            (difficulty,)
        )
        result = self.cursor.fetchone()
        # print(f"Retrieved board for difficulty {difficulty}: {result}")  # Add this line
        return result[0] if result else None




    def save_game_progress(self, level_id, player_board, computer_board, current_turn):
        player_board_str = self.board_to_string(player_board)
        computer_board_str = self.board_to_string(computer_board)
        self.cursor.execute("""
            INSERT INTO game_progress (level_id, player_board, computer_board, current_turn)
            VALUES (?, ?, ?, ?)
        """, (level_id, player_board_str, computer_board_str, current_turn))
        self.conn.commit()
        return self.cursor.lastrowid

    def board_to_string(self, board):
        if isinstance(board, str):
            return board

        ships_str = []
        for ship in board.ships:
            ship_coords = ';'.join([f"{x},{y}" for x, y in ship.positions])
            ships_str.append(f"{ship.size}:{ship_coords}")
        return '|'.join(ships_str)

    def string_to_board(self, board_str, board_size):
        board = Board(board_size)
        if board_str:
            for ship_str in board_str.split('|'):
                size, coords_str = ship_str.split(':')
                coords = [tuple(map(int, coord.split(','))) for coord in coords_str.split(';')]
                ship = Ship(coords)
                board.place_ship(ship)
        return board

    def load_game_progress(self, game_id):
        self.cursor.execute("SELECT * FROM game_progress WHERE id = ?", (game_id,))
        return self.cursor.fetchone()

    def add_move(self, game_id, player, x, y, result):
        self.cursor.execute("""
            INSERT INTO move_history (game_id, player, x, y, result)
            VALUES (?, ?, ?, ?, ?)
        """, (game_id, player, x, y, result))
        self.conn.commit()

    def get_move_history(self, game_id):
        self.cursor.execute("SELECT * FROM move_history WHERE game_id = ?", (game_id,))
        return self.cursor.fetchall()

    def add_to_leaderboard(self, user_id, score, ships_sunk, moves, is_win):
        self.cursor.execute('''
            INSERT OR REPLACE INTO leaderboard
            (user_id, score, wins, losses, total_ships_sunk, total_moves, games_played)
            VALUES (
                ?,
                COALESCE((SELECT score FROM leaderboard WHERE user_id = ?), 0) + ?,
                COALESCE((SELECT wins FROM leaderboard WHERE user_id = ?), 0) + ?,
                COALESCE((SELECT losses FROM leaderboard WHERE user_id = ?), 0) + ?,
                COALESCE((SELECT total_ships_sunk FROM leaderboard WHERE user_id = ?), 0) + ?,
                COALESCE((SELECT total_moves FROM leaderboard WHERE user_id = ?), 0) + ?,
                COALESCE((SELECT games_played FROM leaderboard WHERE user_id = ?), 0) + 1
            )
        ''', (user_id, user_id, score, user_id, 1 if is_win else 0, user_id, 0 if is_win else 1,
            user_id, ships_sunk, user_id, moves, user_id))
        self.conn.commit()

    def get_leaderboard(self, limit=10):
        self.cursor.execute('''
            SELECT users.username, leaderboard.score, leaderboard.wins, leaderboard.losses,
                leaderboard.total_ships_sunk, leaderboard.total_moves, leaderboard.games_played
            FROM leaderboard
            JOIN users ON leaderboard.user_id = users.id
            ORDER BY leaderboard.score DESC LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()
