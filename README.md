# Battleships Game

A classic strategic naval combat game where you compete against the computer to sink all its ships before yours are destroyed. Built with Python and Tkinter, featuring an intuitive GUI interface.

## Overview

Battleships is a turn-based strategy game played on grids where players strategically place ships and take turns guessing enemy ship locations. The first player to sink all opponent ships wins!

## Features

- **Player vs Computer Gameplay** - Challenge the AI opponent
- **Difficulty Levels** - Multiple predefined board configurations for varying challenges
- **Game Statistics** - Track wins, losses, and game metrics
- **User Profiles** - Persistent user data and game history
- **Interactive GUI** - Clean, user-friendly Tkinter interface

## Requirements

- Python 3.7+
- tkinter (usually included with Python)
- sqlite3 (usually included with Python)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Aayush-H/battleships-game.git
   cd battleships-game
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirement.txt
   ```

3. **Initialize the database (first time only):**
   ```bash
   python initialize_db.py
   ```

## Quick Start

Run the game:
```bash
python game.py
```

## How to Play

1. Launch the game and log in or create a new account
2. Choose your difficulty level
3. Place your ships on the grid strategically
4. Take turns guessing coordinates to hit enemy ships
5. Sink all opponent ships to win!

## Project Structure

- **`game.py`** - Main application and game GUI
- **`game_components.py`** - Core game logic (Ship, Board, ComputerPlayer classes)
- **`database_manager.py`** - User data and game statistics management
- **`initialize_db.py`** - Database initialization script
- **`predefined_boards.py`** - Pre-configured boards for different difficulty levels

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests for improvements and bug fixes.

## License

This project is open source and available under the MIT License.