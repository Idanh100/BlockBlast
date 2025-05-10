import pygame
import random
from Block import Block
from State2 import State
from Graphics2 import Graphics

class Environment:
    def __init__(self, state):
        self.state = state
        
        pygame.init()
        info = pygame.display.get_desktop_sizes()[0]  # אם יש כמה מסכים – לוקח את הראשון
        self.width, self.height = info

        self.GRID_ORIGIN_Y = self.height / 10
        self.GRID_SIZE = self.width / 30
        self.GRID_ORIGIN_X = (self.width / 2) - (self.GRID_SIZE * 4)
        self.GRID_MARGIN = 4



    def all_shapes(self):
        """Generate all possible block shapes for the game."""
        return {
            "square": [[1, 1], [1, 1]],
            "line2": [[1, 1]],
            "line3": [[1, 1, 1]],
            "line4": [[1, 1, 1, 1]],
            "line5": [[1, 1, 1, 1, 1]],
            "col2": [[1], [1]],
            "col3": [[1], [1], [1]],
            "col4": [[1], [1], [1], [1]],
            "col5": [[1], [1], [1], [1], [1]],
            "T": [[0, 1, 0], [1, 1, 1]],
            "T_inverted": [[1, 1, 1], [0, 1, 0]],
            "T_right": [[1, 0], [1, 1], [1, 0]],
            "T_left": [[0, 1], [1, 1], [0, 1]],
            "L": [[1, 0], [1, 0], [1, 1]],
            "L_flipped": [[0, 1], [0, 1], [1, 1]],
            "L_rotated": [[1, 1, 1], [1, 0, 0]],
            "L_rotated_flipped": [[1, 1, 1], [0, 0, 1]],
            "Z": [[1, 1, 0], [0, 1, 1]],
            "Z_vertical": [[0, 1], [1, 1], [1, 0]],
            "S": [[0, 1, 1], [1, 1, 0]],
            "S_vertical": [[1, 0], [1, 1], [0, 1]],
            "plus": [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
            "dot": [[1]],
            "small_square": [[1, 1], [1, 1]],
            "corner": [[1, 1], [1, 0]],
            "corner_flipped": [[1, 1], [0, 1]],
            "corner_rotated": [[0, 1], [1, 1]],
            "corner_rotated_flipped": [[1, 0], [1, 1]],
            "U": [[1, 0, 1], [1, 1, 1]],
            "U_rotated": [[1, 1], [1, 0], [1, 1]],
            "U_inverted": [[1, 1, 1], [1, 0, 1]],
            "U_rotated_flipped": [[1, 1], [0, 1], [1, 1]],
            "2x3": [[1, 1, 1], [1, 1, 1]],
            "3x3": [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
        }
    
    def reset(self):
        """
        Reset the game state, including the board and blocks.
        """
        self.state = State()  # יצירת אובייקט חדש של State
        self.set_random_block()  # יצירת בלוקים חדשים
        print("Game has been reset.")
        print(self.state.Board)  # הדפסת הלוח המאופס לצורך בדיקה

    def set_random_block(self, state: State = None):
        """Get a random shape from all available shapes."""
        if state is None:
            state = self.state
        all_shapes = self.all_shapes()
        blocks = random.sample(list(all_shapes.values()), 3)
        blocks_lst = []
        
        start_x = (self.width / 2) - (self.width / 4)  # מיקום X התחלתי
        start_y = self.height / 1.5  # מיקום Y מתחת ללוח
        spacing = self.width / 5  # רווח בין בלוקים

        for i, block in enumerate(blocks):
            rect = pygame.Rect(start_x + i * spacing, start_y, 50, 50)  # מיקום וגודל
            blocks_lst.append(Block(block, rect, i + 1))  # מזהה ייחודי לכל בלוק

        state.Blocks = set(blocks_lst)  

    def move(self, state: State, action: tuple):
        """
        Handle the move action. Place the block on the board if the move is valid,
        otherwise reset the block to its initial position.

        Args:
            state (State): The current game state.
            action (tuple): A tuple containing the block and its drop position.
        """
        block, position = action
        initial_position = block.rect.copy()  # שמירת המיקום ההתחלתי של הבלוק

        # המרת מיקום פיקסלים למיקום רשת
        grid_x = int((position[0] - self.GRID_ORIGIN_X) / self.GRID_SIZE)
        grid_y = int((position[1] - self.GRID_ORIGIN_Y) / self.GRID_SIZE)

        # בדיקת חוקיות המהלך
        if self.is_valid_move(state, block, (grid_x, grid_y)):
            # קיבוע הבלוק ללוח
            self.fix_block_to_board(state, block, (grid_x, grid_y))
            print("Move is valid. Block fixed to the board.")

            # בדיקה אם יש שורות שצריך לפוצץ
            self.check_and_explode_rows(state)
        else:
            # החזרת הבלוק למקומו ההתחלתי
            block.rect = initial_position
            print("Move is invalid. Block reset to initial position.")

        # בדיקה אם צריך ליצור בלוקים חדשים
        self.check_and_generate_blocks()

    def is_valid_move(self, state: State, block: Block, position: tuple) -> bool:
        """
        Check if placing the block at the given position is a valid move.
        
        Args:
            state (State): The current game state.
            block (Block): The block to place.
            position (tuple): The (x, y) position where the block is to be placed.
        
        Returns:
            bool: True if the move is valid, False otherwise.
        """
        board = state.Board
        grid_x, grid_y = position  # המיקום על הלוח (קואורדינטות רשת)

        # עבור כל תא בבלוק
        for y, row in enumerate(block.shape):
            for x, cell in enumerate(row):
                if cell == 1:  # תא פעיל בבלוק
                    board_x = grid_x + x
                    board_y = grid_y + y

                    # בדיקה אם התא חורג מגבולות הלוח
                    if board_x < 0 or board_x >= board.shape[1] or board_y < 0 or board_y >= board.shape[0]:
                        return False

                    # בדיקה אם התא כבר תפוס
                    if board[board_y][board_x] != 0:
                        return False

        return True

    def fix_block_to_board(self, state: State, block: Block, position: tuple):
        """
        Fix the block to the board at the given position, making it immovable.

        Args:
            state (State): The current game state.
            block (Block): The block to fix to the board.
            position (tuple): The (x, y) position where the block is to be fixed.
        """
        board = state.Board
        grid_x, grid_y = position  # המיקום על הלוח (קואורדינטות רשת)
        placed_cells = 0  # סופר את כמות המשבצות שהונחו

        # עדכון הלוח עם הבלוק
        for y, row in enumerate(block.shape):
            for x, cell in enumerate(row):
                if cell == 1:  # תא פעיל בבלוק
                    board_x = grid_x + x
                    board_y = grid_y + y
                    if 0 <= board_x < len(board[0]) and 0 <= board_y < len(board):
                        board[board_y][board_x] = block.color_id  # עדכון התא בלוח עם מזהה הצבע
                        placed_cells += 1  # עדכון כמות המשבצות שהונחו

        # עדכון הניקוד
        state.score += placed_cells

        # הסרת הבלוק מרשימת הבלוקים
        if block in state.Blocks:
            state.Blocks.remove(block)
        print(f"Block fixed to the board. Score increased by {placed_cells}. Total score: {state.score}")

    def check_and_generate_blocks(self):
        """
        Check if there are no more blocks available and generate new ones if needed.
        """
        if not self.state.Blocks:  # אם אין בלוקים ברשימה
            self.set_random_block()
            print("Generated new blocks.")

    def check_and_explode_rows(self, state: State):
        """
        Check for full rows and columns, remove them, and update the score.

        Args:
            state (State): The current game state.
        """
        board = state.Board
        rows_to_explode = []
        cols_to_explode = []

        # בדיקת שורות מלאות
        for y, row in enumerate(board):
            if all(cell != 0 for cell in row):  # אם כל התאים בשורה מלאים
                rows_to_explode.append(y)

        # בדיקת עמודות מלאות
        for x in range(len(board[0])):
            if all(row[x] != 0 for row in board):  # אם כל התאים בעמודה מלאים
                cols_to_explode.append(x)

        # פיצוץ שורות
        for row_index in rows_to_explode:
            board[row_index] = [0] * len(board[row_index])  # ריקון השורה
            state.score += 10  # ניקוד לשורה
            print(f"Row {row_index} exploded! Score increased by 10. Total score: {state.score}")

        # פיצוץ עמודות
        for col_index in cols_to_explode:
            for row in board:
                row[col_index] = 0  # ריקון העמודה
            state.score += 10  # ניקוד לעמודה
            print(f"Column {col_index} exploded! Score increased by 10. Total score: {state.score}")

    def is_game_over(self, state: State) -> bool:
        """
        Check if the game is over. The game ends when there is no space on the board
        to place any of the current blocks.

        Args:
            state (State): The current game state.

        Returns:
            bool: True if the game is over, False otherwise.
        """
        board = state.Board
        for block in state.Blocks:
            for y in range(len(board)):
                for x in range(len(board[0])):
                    if self.is_valid_move(state, block, (x, y)):
                        return False  # יש מקום להניח לפחות בלוק אחד
        return True  # אין מקום להניח אף בלוק


