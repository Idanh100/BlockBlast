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
        if state is None:
            state = self.state
        all_shapes = self.all_shapes()
        blocks = random.sample(list(all_shapes.values()), 3)
        blocks_lst = []
        
        start_x = (self.width / 2) - (self.width / 4)
        start_y = self.height / 1.5
        spacing = self.width / 5

        for i, block in enumerate(blocks):
            rect = pygame.Rect(start_x + i * spacing, start_y, 50, 50)
            new_block = Block(block, rect, i + 1)
            new_block.initial_position = rect.copy()  # שמירת המיקום ההתחלתי
            blocks_lst.append(new_block)

        state.Blocks = set(blocks_lst)

    def move(self, state: State, action: tuple):
        block, position = action

        # המרת מיקום פיקסלים למיקום רשת
        grid_x = int((position[0] - self.GRID_ORIGIN_X) / self.GRID_SIZE)
        grid_y = int((position[1] - self.GRID_ORIGIN_Y) / self.GRID_SIZE)

        # בדיקת חוקיות המהלך
        if self.is_valid_move(state, block, (grid_x, grid_y)):
            self.fix_block_to_board(state, block, (grid_x, grid_y))
            print("Move is valid. Block fixed to the board.")

            # בדיקה אם יש שורות שצריך לפוצץ
            self.check_and_explode_rows(state)
        else:
            # החזרת הבלוק למיקומו ההתחלתי הקבוע
            block.rect = block.initial_position.copy()
            print("Move is invalid. Block reset to its initial position.")

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
        Check for full rows or columns, explode them, and update the score.
        """
        board = state.Board
        rows_to_explode = [y for y in range(board.shape[0]) if all(board[y, :] != 0)]
        cols_to_explode = [x for x in range(board.shape[1]) if all(board[:, x] != 0)]

        # פיצוץ שורות
        for row in rows_to_explode:
            board[row, :] = 0

        # פיצוץ עמודות
        for col in cols_to_explode:
            board[:, col] = 0

        # עדכון ניקוד
        num_explosions = len(rows_to_explode) + len(cols_to_explode)
        if num_explosions > 0:
            state.turns_since_last_explosion = 0  # איפוס ספירת התורות
            if state.in_combo:
                state.combo_count += num_explosions
            else:
                state.combo_count = num_explosions

            # חישוב ניקוד Combo
            for i in range(num_explosions):
                state.score += (state.combo_count + i) * 10

            state.in_combo = True  # הפעלת Combo
        else:
            state.turns_since_last_explosion += 1
            if state.turns_since_last_explosion > 2:  # סיום Combo לאחר 2 תורות ללא פיצוץ
                state.in_combo = False
                state.combo_count = 0

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


