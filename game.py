import hashlib
import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from turtle import width
from game_components import Ship, Board, ComputerPlayer
from database_manager import DatabaseManager

class BattleshipsGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Battleships Game")
        self.master.geometry("850x600")  # Set a consistent window size

        # Define styles
        self.BUTTON_FONT = ("Helvetica", 12)
        self.LABEL_FONT = ("Helvetica", 14)
        self.TITLE_FONT = ("Helvetica", 18, "bold")
        self.BG_COLOR = "#f0f0f0"
        self.BUTTON_COLOR = "#4CAF50"
        self.BUTTON_TEXT_COLOR = "white"

        # Create and configure ttk styles
        self.style = ttk.Style()
        self.style.theme_use('clam')  # You can change this to 'alt', 'default', 'classic' etc.

        self.style.configure('TButton', font=('Helvetica', 12), padding=5)
        self.style.configure('TLabel', font=('Helvetica', 12))
        self.style.configure('Title.TLabel', font=('Helvetica', 18, 'bold'))

        # Create custom styles
        self.style.configure('Menu.TButton', font=('Helvetica', 14), width=20,padding=10)
        #self.style.configure('Game.TButton', width=2, padding=1)
        # In the __init__ method, add these new styles
        self.style.configure('Hit.TLabel', foreground='red')
        self.style.configure('Miss.TLabel', foreground='blue')

         # Create custom styles for game buttons
        self.style.configure('Game.TButton', width=2, padding=1)
        self.style.map('Game.TButton',
                    background=[('active', '#d9d9d9'), ('disabled', '#f0f0f0')])

        self.style.configure('Hit.TButton', background='red', foreground='white',width=2,padding=1)
        self.style.map('Hit.TButton',
                    background=[('active', 'dark red'), ('disabled', 'red')])

        self.style.configure('Miss.TButton', background='blue', foreground='white',width=2,padding=1)
        self.style.map('Miss.TButton',
                    background=[('active', 'dark blue'), ('disabled', 'blue')])

        self.style.configure('Ship.TButton', background='gray',width=2,padding=1)
        self.style.map('Ship.TButton',
                    background=[('active', 'dark gray'), ('disabled', 'gray')])



        self.db_manager = DatabaseManager()
        self.db_manager.initialize_default_levels()  # Initialize default levels
        self.board_size = 10
        self.ships_to_place = [Ship(5), Ship(4), Ship(3), Ship(3), Ship(2)]
        self.current_ship_index = 0

        self.ships_to_place = [Ship(5), Ship(4), Ship(3), Ship(3), Ship(2)]
        self.current_ship_index = 0

        self.game_id = None  # Initialize game_id as None
        self.current_user = None
        self.game_start_time = None
        self.hits = 0
        self.misses = 0
        self.ships_sunk = 0
        self.ship_configuration = [5, 4, 3, 3, 2]  # Default configuration
        self.difficulty = 'medium'  # Default difficulty
        self.game_duration = 0

        self.create_main_menu()

    def create_main_menu(self):
    # Clear the window
        for widget in self.master.winfo_children():
            widget.destroy()

        main_frame = ttk.Frame(self.master, padding="20 20 20 20")
        main_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(main_frame, text="Battleships Game", style='Title.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 20))

        if self.current_user:
            ttk.Label(main_frame, text=f"Welcome, {self.current_user[1]}!").grid(row=1, column=0, columnspan=2, pady=(0, 20))

            buttons = [
                ("New Game", self.new_game),
                ("Load Game", self.load_game),
                ("Settings", self.show_settings),
                ("View Statistics", self.show_statistics),
                ("View Leaderboard", self.show_leaderboard),
                ("How to Play", self.show_how_to_play),
                ("Logout", self.logout)
            ]

            for i, (text, command) in enumerate(buttons):
                ttk.Button(main_frame, text=text, command=command, style='Menu.TButton').grid(
                    row=i//2 + 2, column=i%2, padx=10, pady=5, sticky="ew")

        else:
            buttons = [
                ("Login", self.show_login),
                ("Register", self.show_register),
                ("How to Play", self.show_how_to_play)
            ]

            for i, (text, command) in enumerate(buttons):
                ttk.Button(main_frame, text=text, command=command, style='Menu.TButton').grid(
                    row=i+1, column=0, columnspan=2, pady=5, sticky="ew")

        ttk.Button(main_frame, text="Exit", command=self.master.quit, style='Menu.TButton').grid(
            row=len(buttons)+2, column=0, columnspan=2, pady=(20, 0), sticky="ew")

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

    def show_login(self):
    # Clear the window
        for widget in self.master.winfo_children():
            widget.destroy()

        login_frame = ttk.Frame(self.master, padding="20 20 20 20")
        login_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(login_frame, text="Login", style='Title.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 20))

        ttk.Label(login_frame, text="Username:").grid(row=1, column=0, sticky="e", padx=(0, 10))
        username_entry = ttk.Entry(login_frame,width=20)
        username_entry.grid(row=1, column=1, sticky="ew")

        ttk.Label(login_frame, text="Password:").grid(row=2, column=0, sticky="e", padx=(0, 10))
        password_entry = ttk.Entry(login_frame, show="*",width=20)
        password_entry.grid(row=2, column=1, sticky="ew")

        ttk.Button(login_frame, text="Login", command=lambda: self.login(username_entry.get(), password_entry.get()),
                style='Menu.TButton').grid(row=3, column=0, columnspan=2, pady=(20, 10))

        ttk.Button(login_frame, text="Back", command=self.create_main_menu,
                style='Menu.TButton').grid(row=4, column=0, columnspan=2)

        login_frame.grid_columnconfigure(1, weight=1)

    def login(self, username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user = self.db_manager.get_user(username, hashed_password)
        if user:
            self.current_user = user
            preferences = self.db_manager.get_user_preferences(user[0])
            self.board_size = preferences['board_size']
            self.ship_configuration = [int(s) for s in preferences['ship_configuration'].split(',')]
            self.difficulty = preferences['difficulty']
            messagebox.showinfo("Login Successful", f"Welcome, {username}!")
            self.create_main_menu()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def show_register(self):
        # Clear the window
        for widget in self.master.winfo_children():
            widget.destroy()

        tk.Label(self.master, text="Username:").pack(pady=5)
        username_entry = tk.Entry(self.master)
        username_entry.pack(pady=5)

        tk.Label(self.master, text="Password:").pack(pady=5)
        password_entry = tk.Entry(self.master, show="*")
        password_entry.pack(pady=5)

        tk.Label(self.master, text="Email:").pack(pady=5)
        email_entry = tk.Entry(self.master)
        email_entry.pack(pady=5)

        tk.Button(self.master, text="Register", command=lambda: self.register(username_entry.get(), password_entry.get(), email_entry.get())).pack(pady=10)
        tk.Button(self.master, text="Back", command=self.create_main_menu).pack(pady=10)

    def show_how_to_play(self):
    # Clear the window
        for widget in self.master.winfo_children():
            widget.destroy()

        how_to_play_frame = ttk.Frame(self.master, padding="20 20 20 20")
        how_to_play_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(how_to_play_frame, text="How to Play Battleships", style='Title.TLabel').pack(pady=(0, 20))

        instructions = [
            "1. Setup Phase:",
            "   - Place your ships on your board.",
            "   - Ships cannot overlap or extend beyond the board.",
            "",
            "2. Gameplay:",
            "   - Players take turns guessing coordinates to attack.",
            "   - Coordinates are given as letter-number pairs (e.g., A5, C3).",
            "   - If a ship is hit, it's marked in red. Misses are marked in blue.",
            "",
            "3. Ship Fleet:",
            "   - 1 Carrier (5 spaces)",
            "   - 1 Battleship (4 spaces)",
            "   - 1 Cruiser (3 spaces)",
            "   - 1 Submarine (3 spaces)",
            "   - 1 Destroyer (2 spaces)",
            "",
            "4. Winning the Game:",
            "   - Sink all of your opponent's ships before they sink yours!",
            "",
            "5. Scoring:",
            "   - Score is based on accuracy and speed.",
            "   - Hitting enemy ships increases your score.",
            "   - Taking fewer turns results in a higher score."
        ]

        text_widget = tk.Text(how_to_play_frame, wrap=tk.WORD, width=60, height=20, font=('Helvetica', 10))
        text_widget.pack(pady=10, padx=20, expand=True, fill=tk.BOTH)

        for line in instructions:
            text_widget.insert(tk.END, line + "\n")

        text_widget.config(state=tk.DISABLED)  # Make the text widget read-only

        # Create a scrollbar
        scrollbar = ttk.Scrollbar(how_to_play_frame, orient="vertical", command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        text_widget.configure(yscrollcommand=scrollbar.set)

        ttk.Button(how_to_play_frame, text="Back to Main Menu", command=self.create_main_menu, style='Menu.TButton').pack(pady=10)

    def show_settings(self):
    # Clear the window
        for widget in self.master.winfo_children():
            widget.destroy()

        settings_frame = ttk.Frame(self.master, padding="20 20 20 20")
        settings_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(settings_frame, text="Game Settings", style='Title.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Board Size
        ttk.Label(settings_frame, text="Board Size:").grid(row=1, column=0, sticky="e", padx=(0, 10))
        size_var = tk.StringVar(value=str(self.board_size))
        size_options = ["8", "10", "12"]
        size_menu = ttk.Combobox(settings_frame, textvariable=size_var, values=size_options, state="readonly")
        size_menu.grid(row=1, column=1, sticky="w")

        # Ship Configuration
        ttk.Label(settings_frame, text="Ship Configuration:").grid(row=2, column=0, sticky="ne", padx=(0, 10), pady=(10, 0))
        ship_frame = ttk.Frame(settings_frame)
        ship_frame.grid(row=2, column=1, sticky="w", pady=(10, 0))

        ship_entries = []
        for i, size in enumerate(self.ship_configuration):
            ttk.Label(ship_frame, text=f"Ship {i+1} size:").grid(row=i, column=0, sticky="e", padx=(0, 5))
            entry = ttk.Entry(ship_frame, width=5)
            entry.insert(0, str(size))
            entry.grid(row=i, column=1, pady=2)
            ship_entries.append(entry)

        # Add/Remove Ship buttons
        button_frame = ttk.Frame(settings_frame)
        button_frame.grid(row=3, column=1, sticky="w", pady=(10, 0))

        def add_ship():
            if len(ship_entries) < 10:  # Limit to 10 ships
                i = len(ship_entries)
                ttk.Label(ship_frame, text=f"Ship {i+1} size:").grid(row=i, column=0, sticky="e", padx=(0, 5))
                entry = ttk.Entry(ship_frame, width=5)
                entry.insert(0, "2")  # Default new ship size
                entry.grid(row=i, column=1, pady=2)
                ship_entries.append(entry)

        def remove_ship():
            if len(ship_entries) > 1:  # Always keep at least one ship
                entry = ship_entries.pop()
                entry.grid_forget()
                entry.destroy()
                ship_frame.grid_slaves(row=len(ship_entries))[0].grid_forget()
                ship_frame.grid_slaves(row=len(ship_entries))[0].destroy()

        ttk.Button(button_frame, text="Add Ship", command=add_ship).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Remove Ship", command=remove_ship).grid(row=0, column=1)

        # Difficulty
        ttk.Label(settings_frame, text="Difficulty:").grid(row=4, column=0, sticky="e", padx=(0, 10), pady=(10, 0))
        difficulty_var = tk.StringVar(value=self.difficulty)
        difficulty_options = ["easy", "medium", "hard"]
        difficulty_menu = ttk.Combobox(settings_frame, textvariable=difficulty_var, values=difficulty_options, state="readonly")
        difficulty_menu.grid(row=4, column=1, sticky="w", pady=(10, 0))

        def save_settings():
            if not self.current_user:
                messagebox.showerror("Error", "Please login to save settings")
                return
            new_size = int(size_var.get())
            new_ship_config = ','.join([entry.get() for entry in ship_entries])
            new_difficulty = difficulty_var.get()

            self.board_size = new_size
            self.ship_configuration = [int(s) for s in new_ship_config.split(',')]
            self.difficulty = new_difficulty

            self.db_manager.set_user_preferences(
                self.current_user[0], new_size, new_ship_config, new_difficulty
            )
            messagebox.showinfo("Settings Saved", "Your settings have been saved.")
            self.create_main_menu()

        ttk.Button(settings_frame, text="Save", command=save_settings, style='Menu.TButton').grid(row=5, column=0, columnspan=2, pady=(20, 10))
        ttk.Button(settings_frame, text="Back", command=self.create_main_menu, style='Menu.TButton').grid(row=6, column=0, columnspan=2)

        # Configure grid weights
        settings_frame.grid_columnconfigure(1, weight=1)
        for i in range(7):
            settings_frame.grid_rowconfigure(i, weight=1)

    def update_game_duration(self):
        if self.game_start_time is not None:
            self.game_duration = time.time() - self.game_start_time

    def register(self, username, password, email):
        if not username or not password or not email:
            messagebox.showerror("Registration Failed", "All fields are required")
            return

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if self.db_manager.add_user(username, hashed_password, email):
            messagebox.showinfo("Registration Successful", "You can now login with your new account")
            self.create_main_menu()
        else:
            messagebox.showerror("Registration Failed", "Username or email already exists")

    def logout(self):
        self.current_user = None
        self.create_main_menu()

    def new_game(self):
        if not self.current_user:
            messagebox.showerror("Error", "Please login to start a new game")
            return

        # Implement level selection
        levels = self.db_manager.get_levels()

        # Clear the window
        for widget in self.master.winfo_children():
            widget.destroy()

        level_frame = ttk.Frame(self.master, padding="20 20 20 20")
        level_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(level_frame, text="Select a level:", style='Title.TLabel').pack(pady=10)

        for level_id, level_name in levels:
            ttk.Button(level_frame, text=level_name, command=lambda id=level_id: self.start_game(id), style='Menu.TButton').pack(pady=5)

        ttk.Button(level_frame, text="Back", command=self.create_main_menu, style='Menu.TButton').pack(pady=10)




    def start_game(self, level_id):
        self.level_id = level_id
        self.player_board = Board(self.board_size)
        self.ships_to_place = [Ship(size) for size in self.ship_configuration]

        # Set difficulty based on user preferences or default to 'medium'
        if self.current_user:
            user_preferences = self.db_manager.get_user_preferences(self.current_user[0])
            self.difficulty = user_preferences['difficulty']
        else:
            self.difficulty = 'medium'  # Default difficulty if user is not logged in

        # print(f"Starting game with difficulty: {self.difficulty}")  # Add this line

        self.computer_player = ComputerPlayer(self.board_size, self.difficulty)

        self.computer_board = self.computer_player.place_ships(self.ships_to_place.copy())


        # Get a predefined board for the computer
        predefined_board = self.db_manager.get_random_predefined_board(self.difficulty)
        if predefined_board:
            # print(f"Got a predefined board: {predefined_board}")
            self.computer_board = Board(self.board_size)
            self.place_ships_from_coordinates(self.computer_board, predefined_board)
        else:
            # print("No predefined board found, using random placement")
            self.computer_player = ComputerPlayer(self.board_size, self.difficulty)
            self.computer_board = self.computer_player.place_ships(self.ships_to_place.copy())

        # print("Computer board after setup:")
        # print(self.computer_board)

        # Create a new game entry in the database and store the game_id
        self.game_id = self.db_manager.save_game_progress(
            self.level_id,
            str(self.player_board),
            str(self.computer_board),
            0  # Starting turn
        )
        self.game_start_time = time.time()
        self.game_duration = 0
        self.turns = 0
        self.hits = 0
        self.misses = 0
        self.ships_sunk = 0
        messagebox.showinfo("Game Started", f"Starting game with level ID: {level_id}")
        self.create_placement_screen()

    # def place_ships_from_coordinates(self, board, coordinates):
    #     print('got coordinates')
    #     for ship_data in coordinates.split('|'):
    #         print('found coordinates to place ship')
    #         ship_type, coords = ship_data.split(':')
    #         ship_coords = [tuple(map(int, coord.split(','))) for coord in coords.split(';')]
    #         ship = Ship(ship_coords)
    #         board.place_ship(ship)

    def place_ships_from_coordinates(self, board, coordinates):
        for ship_data in coordinates.split('|'):
            size, coords = ship_data.split(':')
            ship_coords = [tuple(map(int, coord.split(','))) for coord in coords.split(';')]
            ship = Ship(int(size))
            ship.positions = ship_coords
            board.place_ship(ship)
        # print(f"Board after placing ships: {board}")  # Add this line

    def create_placement_screen(self):
        # Clear the window
        for widget in self.master.winfo_children():
            widget.destroy()

        self.placement_frame = ttk.Frame(self.master)
        self.placement_frame.pack()

        # Create column labels (A, B, C, ...)
        for i in range(self.board_size):
            tk.Label(self.placement_frame, text=chr(65+i)).grid(row=0, column=i+1)

        # Create row labels (1, 2, 3, ...)
        for i in range(self.board_size):
            tk.Label(self.placement_frame, text=str(i+1)).grid(row=i+1, column=0)

        # Create the board buttons
        self.board_buttons = []
        for i in range(self.board_size):
            row = []
            for j in range(self.board_size):
                btn = ttk.Button(self.placement_frame, text='', style='Game.TButton',
                             command=lambda x=i, y=j: self.place_ship(x, y))
                btn.grid(row=i+1, column=j+1, padx=1, pady=1)
                row.append(btn)
            self.board_buttons.append(row)

        # Create orientation selection
        self.orientation_var = tk.StringVar(value="horizontal")
        tk.Radiobutton(self.master, text="Horizontal", variable=self.orientation_var, value="horizontal").pack()
        tk.Radiobutton(self.master, text="Vertical", variable=self.orientation_var, value="vertical").pack()
        tk.Button(self.master, text="Reset Placement", command=self.reset_placement).pack()

        # Display current ship information
        current_ship = self.ships_to_place[self.current_ship_index]
        ship_size = len(current_ship) if isinstance(current_ship, list) else current_ship.size
        self.ship_info_label = tk.Label(self.master, text=f"Place ship of size {self.ships_to_place[self.current_ship_index].size}")
        self.ship_info_label.pack()

    def place_ship(self, x, y):
        current_ship = self.ships_to_place[self.current_ship_index]
        orientation = self.orientation_var.get()

        # Generate the positions based on the ship's size, start position, and orientation
        if orientation == "horizontal":
            positions = [(x, y+i) for i in range(current_ship.size)]
        else:  # vertical
            positions = [(x+i, y) for i in range(current_ship.size)]

        # Check if the ship is within the board boundaries
        if all(0 <= sx < self.board_size and 0 <= sy < self.board_size for sx, sy in positions):
            # Set the positions for the current ship
            current_ship.positions = positions

            if self.player_board.place_ship(current_ship):
                for sx, sy in positions:
                    #self.board_buttons[sx][sy].config(bg='gray')
                    self.board_buttons[sx][sy].configure(style='Ship.TButton')

                self.current_ship_index += 1
                if self.current_ship_index < len(self.ships_to_place):
                    self.ship_info_label.config(text=f"Place ship of size {self.ships_to_place[self.current_ship_index].size}")
                else:
                    self.start_gameplay()
            else:
                messagebox.showerror("Invalid Placement", "Cannot place ship here. Try again.")
        else:
            messagebox.showerror("Invalid Placement", "Ship is outside the board. Try again.")

    def reset_placement(self):
        self.current_ship_index = 0
        self.player_board = Board(self.board_size)
        self.create_placement_screen()

    def start_gameplay(self):
        self.player_turn = True
        self.game_over = False
        self.create_game_screen()

    def create_game_screen(self):
    # Clear the window
        for widget in self.master.winfo_children():
            widget.destroy()

        game_frame = ttk.Frame(self.master, padding="20 20 20 20")
        game_frame.pack(expand=True, fill=tk.BOTH)

        # Create frames for player and computer boards
        player_frame = ttk.Frame(game_frame)
        player_frame.grid(row=0, column=0, padx=(0, 20))

        computer_frame = ttk.Frame(game_frame)
        computer_frame.grid(row=0, column=1)

        # Create labels for the boards
        ttk.Label(player_frame, text="Your Board", style='Title.TLabel').grid(row=0, column=0, columnspan=self.board_size)
        ttk.Label(computer_frame, text="Computer's Board", style='Title.TLabel').grid(row=0, column=0, columnspan=self.board_size)

        # Create column labels (A, B, C, ...)
        for i in range(self.board_size):
            ttk.Label(player_frame, text=chr(65+i)).grid(row=1, column=i+1)
            ttk.Label(computer_frame, text=chr(65+i)).grid(row=1, column=i+1)

        # Create row labels (1, 2, 3, ...)
        for i in range(self.board_size):
            ttk.Label(player_frame, text=str(i+1)).grid(row=i+2, column=0)
            ttk.Label(computer_frame, text=str(i+1)).grid(row=i+2, column=0)

        # Create buttons for the player's board (display only)
        self.player_buttons = []
        for i in range(self.board_size):
            row = []
            for j in range(self.board_size):
                btn = ttk.Button(player_frame, text='', style='Game.TButton', state='disabled')
                btn.grid(row=i+2, column=j+1)
                if self.player_board.grid[i][j] == 'S':
                    btn.configure(style='Ship.TButton')
                row.append(btn)
            self.player_buttons.append(row)

        # Create buttons for the computer's board (interactive)
        self.computer_buttons = []
        for i in range(self.board_size):
            row = []
            for j in range(self.board_size):
                btn = ttk.Button(computer_frame, text='', style='Game.TButton',
                                command=lambda x=i, y=j: self.player_attack(x, y))
                btn.grid(row=i+2, column=j+1)
                # # Debug: Show computer's ships (remove in production)
                # if self.computer_board.grid[i][j] == 'S':
                #     btn.configure(style='Ship.TButton')
                # row.append(btn)
                row.append(btn)
            self.computer_buttons.append(row)

        # Create a label to show whose turn it is
        self.turn_label = ttk.Label(game_frame, text="Your turn", style='Title.TLabel')
        self.turn_label.grid(row=1, column=0, columnspan=2, pady=(20, 0))

        # Create a button to end the game
        ttk.Button(game_frame, text="End Game", command=self.end_game, style='Menu.TButton').grid(row=2, column=0, columnspan=2, pady=(20, 0))

    def player_attack(self, x, y):
        if not self.player_turn or self.game_over:
            return

        self.turns += 1
        result = self.computer_board.receive_attack(x, y)
        btn = self.computer_buttons[x][y]

        if result == 'hit':
            btn.configure(style='Hit.TButton', state='disabled')
            # messagebox.showinfo("Hit!", "You hit a ship!")
            self.hits += 1
            if self.computer_board.is_ship_sunk(x, y):
                self.ships_sunk += 1
            # btn.config(bg='red', state='disabled')
            # messagebox.showinfo("Hit!", "You hit a ship!")
        elif result == 'miss':
            btn.configure(style='Miss.TButton', state='disabled')
            # messagebox.showinfo("Miss", "You missed.")
            self.misses += 1
            # btn.config(bg='blue', state='disabled')
            # messagebox.showinfo("Miss", "You missed.")
        else:
            messagebox.showinfo("Invalid Move", "You've already attacked this position.")
            return
        self.update_game_duration()
        self.db_manager.add_move(self.game_id, 'player', x, y, result)

        if self.computer_board.all_ships_sunk():
            self.game_over = True
            self.update_game_duration()
            if self.current_user:
                score = self.calculate_score()
                self.save_game_results(score, True)
            messagebox.showinfo("Victory!", "You've sunk all the computer's ships!")
            self.show_post_game_screen()
        else:
            self.player_turn = False
            self.turn_label.config(text="Computer's turn")
            self.master.after(1000, self.computer_attack)

    def computer_attack(self):
        x, y = self.computer_player.make_move(self.player_board)
        result = self.player_board.receive_attack(x, y)

        self.turns += 1
        message = f"Computer attacked ({x}, {y}). "

        # Update the player's board visually
        btn = self.player_buttons[x][y]
        if result == 'hit':
            #btn.config(bg='red')
            btn.configure(style='Hit.TButton')
            message += "It's a hit!"
        elif result == 'miss':
            #btn.config(bg='blue')
            btn.configure(style='Miss.TButton')
            message += "It's a miss."

        # messagebox.showinfo("Computer's Move", message)

        self.db_manager.add_move(self.game_id, 'computer', x, y, result)
        self.update_game_duration()

        if self.player_board.all_ships_sunk():
            self.game_over = True
            self.update_game_duration()
            if self.current_user:
                score = self.calculate_score()
                self.save_game_results(score, False)
            messagebox.showinfo("Defeat", "The computer has sunk all your ships!")
            self.show_post_game_screen()
        else:
            self.player_turn = True
            self.turn_label.config(text="Your turn")

    def show_leaderboard(self):
    # Clear the window
        for widget in self.master.winfo_children():
            widget.destroy()

        leaderboard_frame = ttk.Frame(self.master, padding="20 20 20 20")
        leaderboard_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(leaderboard_frame, text="Leaderboard", style='Title.TLabel').pack(pady=10)

        leaderboard_data = self.db_manager.get_leaderboard()

        # Create a frame for the leaderboard table
        table_frame = ttk.Frame(leaderboard_frame)
        table_frame.pack(pady=10)

        headers = ["Rank", "Username", "Score", "Wins", "Losses", "Ships Sunk", "Avg Moves"]
        for i, header in enumerate(headers):
            ttk.Label(table_frame, text=header, style='Title.TLabel').grid(row=0, column=i, padx=5, pady=5)

        for i, (username, score, wins, losses, ships_sunk, total_moves, games_played) in enumerate(leaderboard_data, 1):
            avg_moves = total_moves / games_played if games_played > 0 else 0
            ttk.Label(table_frame, text=f"{i}").grid(row=i, column=0, padx=5, pady=2)
            ttk.Label(table_frame, text=username).grid(row=i, column=1, padx=5, pady=2)
            ttk.Label(table_frame, text=str(score)).grid(row=i, column=2, padx=5, pady=2)
            ttk.Label(table_frame, text=str(wins)).grid(row=i, column=3, padx=5, pady=2)
            ttk.Label(table_frame, text=str(losses)).grid(row=i, column=4, padx=5, pady=2)
            ttk.Label(table_frame, text=str(ships_sunk)).grid(row=i, column=5, padx=5, pady=2)
            ttk.Label(table_frame, text=f"{avg_moves:.2f}").grid(row=i, column=6, padx=5, pady=2)

        ttk.Button(leaderboard_frame, text="Back", command=self.create_main_menu, style='Menu.TButton').pack(pady=10)

    def end_game(self):
        if messagebox.askyesno("End Game", "Are you sure you want to end the game?"):
            self.update_game_duration()
            if self.current_user:
                score = self.calculate_score()
                is_win = self.computer_board.all_ships_sunk()
                self.save_game_results(score, is_win)
            else:
                messagebox.showwarning("Not Logged In", "Game results won't be saved as you're not logged in.")
            self.show_post_game_screen()

    def save_game_results(self, score, is_win):
        if not self.current_user:
            print("Cannot save game results: User not logged in")
            return
        try:
            self.db_manager.add_to_leaderboard(
                self.current_user[0],
                score,
                self.ships_sunk,
                self.turns,
                is_win
            )
            self.db_manager.add_game_statistics(
                self.current_user[0],
                self.turns,
                self.hits,
                self.misses,
                self.ships_sunk,
                self.game_duration
            )
            print("Game results saved successfully")
        except Exception as e:
            print(f"Error saving game results: {str(e)}")
            messagebox.showerror("Error", "Failed to save game results. Please try again.")

    def calculate_score(self):
        total_moves = len(self.db_manager.get_move_history(self.game_id))
        player_hits = sum(1 for move in self.db_manager.get_move_history(self.game_id)
                        if move[2] == 'player' and move[5] == 'hit')

        # Calculate accuracy
        accuracy = player_hits / total_moves if total_moves > 0 else 0

        # Base score calculation
        base_score = player_hits * 100 - (total_moves - player_hits) * 10

        # Difficulty multiplier
        difficulty_multiplier = {
            'easy': 1,
            'medium': 1.5,
            'hard': 2
        }.get(self.difficulty, 1)

        # Time factor (faster games get higher scores)
        time_factor = max(1, 2 - (self.game_duration / 300))  # 300 seconds (5 minutes) as a baseline

        # Ships sunk bonus
        ships_sunk_bonus = self.ships_sunk * 50

        # Calculate final score
        final_score = int((base_score * difficulty_multiplier * time_factor) + ships_sunk_bonus)

        # Accuracy bonus (if accuracy is over 50%, add bonus points)
        if accuracy > 0.5:
            accuracy_bonus = int((accuracy - 0.5) * 200)
            final_score += accuracy_bonus

        return max(0, final_score)  # Ensure the score is never negative

    def show_statistics(self):
        if not self.current_user:
            messagebox.showerror("Error", "Please login to view statistics")
            return

        stats = self.db_manager.get_user_statistics(self.current_user[0])
        if stats:
            games_played, avg_accuracy, avg_time, total_ships_sunk, fastest_game = stats

            # Clear the window
            for widget in self.master.winfo_children():
                widget.destroy()

            stats_frame = ttk.Frame(self.master, padding="20 20 20 20")
            stats_frame.pack(expand=True, fill=tk.BOTH)

            ttk.Label(stats_frame, text="Your Statistics", style='Title.TLabel').pack(pady=10)

            stat_items = [
                f"Games Played: {games_played}",
                f"Average Accuracy: {avg_accuracy:.2f}%",
                f"Average Game Time: {avg_time:.2f} seconds",
                f"Total Ships Sunk: {total_ships_sunk}",
                f"Fastest Game: {fastest_game:.2f} seconds"
            ]

            for item in stat_items:
                ttk.Label(stats_frame, text=item).pack()

            ttk.Button(stats_frame, text="Back", command=self.create_main_menu, style='Menu.TButton').pack(pady=10)
        else:
            messagebox.showinfo("No Statistics", "You haven't played any games yet!")

    def show_post_game_screen(self):
    # Clear the window
        for widget in self.master.winfo_children():
            widget.destroy()

        post_game_frame = ttk.Frame(self.master, padding="20 20 20 20")
        post_game_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(post_game_frame, text="Game Over", style='Title.TLabel').pack(pady=10)

        # Display game statistics
        player_hits = sum(1 for move in self.db_manager.get_move_history(self.game_id)
                        if move[2] == 'player' and move[5] == 'hit')
        computer_hits = sum(1 for move in self.db_manager.get_move_history(self.game_id)
                            if move[2] == 'computer' and move[5] == 'hit')
        total_moves = len(self.db_manager.get_move_history(self.game_id))
        score = self.calculate_score()

        stats = [
            f"Total Moves: {total_moves}",
            f"Player Hits: {player_hits}",
            f"Computer Hits: {computer_hits}",
            f"Final Score: {score}",
            f"Ships Sunk: {self.ships_sunk}",
            f"Hits: {self.hits}",
            f"Misses: {self.misses}",
            f"Game Duration: {self.game_duration:.2f} seconds"
        ]

        for stat in stats:
            ttk.Label(post_game_frame, text=stat).pack()

        # Create a frame for the moves log table
        table_frame = ttk.Frame(post_game_frame)
        table_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Create a canvas and scrollbar for the table
        canvas = tk.Canvas(table_frame)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create table headers
        headers = ["Move", "Player Move", "Computer Move"]
        for col, header in enumerate(headers):
            ttk.Label(scrollable_frame, text=header, style='Title.TLabel').grid(row=0, column=col, padx=5, pady=5)

        # Populate the table with move history
        move_history = self.db_manager.get_move_history(self.game_id)
        player_moves = [move for move in move_history if move[2] == 'player']
        computer_moves = [move for move in move_history if move[2] == 'computer']

        for i in range(max(len(player_moves), len(computer_moves))):
            ttk.Label(scrollable_frame, text=str(i+1)).grid(row=i+1, column=0, padx=5, pady=2)

            if i < len(player_moves):
                player_move = player_moves[i]
                style = 'Hit.TLabel' if player_move[5] == 'hit' else 'Miss.TLabel'
                ttk.Label(scrollable_frame, text=f"({player_move[3]}, {player_move[4]})", style=style).grid(row=i+1, column=1, padx=5, pady=2)

            if i < len(computer_moves):
                computer_move = computer_moves[i]
                style = 'Hit.TLabel' if computer_move[5] == 'hit' else 'Miss.TLabel'
                ttk.Label(scrollable_frame, text=f"({computer_move[3]}, {computer_move[4]})", style=style).grid(row=i+1, column=2, padx=5, pady=2)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Button(post_game_frame, text="Return to Main Menu", command=self.create_main_menu, style='Menu.TButton').pack(pady=10)

    def load_game(self):
        if not self.current_user:
            messagebox.showerror("Error", "Please login to load a game")
            return
        # Implement game loading from database
        # For now, we'll just show a message
        messagebox.showinfo("Load Game", "Game loading not implemented yet")

if __name__ == "__main__":
    root = tk.Tk()
    game = BattleshipsGame(root)
    root.mainloop()