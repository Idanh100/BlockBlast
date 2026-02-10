import pygame
import random
import copy
import numpy as np
from types import SimpleNamespace
from Block import Block
from State2 import State
from Graphics2 import Graphics
import torch

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
        # track explosions and last pre-placement sum for reward calculation
        self.num_explosions = 0
        self.last_preplacement_sum = 0

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
            "dot1": [[1]],
            "dot2": [[1]],
            "dot3": [[1]],
            "dot4": [[1]],
            "dot6": [[1]],
            "dot7": [[1]],
            "dot8": [[1]],
            "dot9": [[1]],
            "dot10": [[1]],
            "dot11": [[1]],
            "dot12": [[1]],
            "dot13": [[1]],
            "dot14": [[1]],
            "dot15": [[1]],
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
            # count occupied cells in the rows/cols covered by the shape BEFORE placement
            self.Get_Reward(state, block, grid_x, grid_y)  # calculate reward before fixing block
            filled_count = self.sum_ones_in_affected_rows_cols(state, block, (grid_x, grid_y))
            self.fix_block_to_board(state, block, (grid_x, grid_y))
            self.print_block_squares(block.shape)

            # בדיקה אם יש שורות שצריך לפוצץ
            num_expl = self.check_and_explode_rows(state)
            self.num_explosions = num_expl
        else:
            # החזרת הבלוק למיקומו ההתחלתי הקבוע
            block.rect = block.initial_position.copy()

        # בדיקה אם צריך ליצור בלוקים חדשים
        self.check_and_generate_blocks()
        # (no per-turn print here)
        return filled_count
    
    def move_legal(self, state: State, action: tuple):
        block, position = action

        # המרת מיקום פיקסלים למיקום רשת
        grid_x = int((position[0] - self.GRID_ORIGIN_X) / self.GRID_SIZE)
        grid_y = int((position[1] - self.GRID_ORIGIN_Y) / self.GRID_SIZE)
        # count before placing so the block's own cells are not included
        filled_count = self.sum_ones_in_affected_rows_cols(state, block, (grid_x, grid_y))
        self.fix_block_to_board(state, block, (grid_x, grid_y))
        self.check_and_explode_rows(state)
        self.check_and_generate_blocks()
        reward = self.reward()
        # (no per-turn print here)
        return reward

    def Get_Reward_Args(self, state: State, action: tuple):
        block, position = action

        # המרת מיקום פיקסלים למיקום רשת
        grid_x = int((position[0] - self.GRID_ORIGIN_X) / self.GRID_SIZE)
        grid_y = int((position[1] - self.GRID_ORIGIN_Y) / self.GRID_SIZE)

        if self.is_valid_move(state, block, (grid_x, grid_y)):
            reward = self.Get_Reward(state, block, grid_x, grid_y)
        else:
            reward = 0
        return reward

    def Get_Reward(self, state, block, grid_x, grid_y):
        reward = self.count_squares_of_block(block.shape)  # נקודות לפי כמות המשבצות שהונחו
        reward += self.sum_ones_in_affected_rows_cols(state, block, (grid_x, grid_y))  # נקודות לפי כמות המשבצות שהיו לפני ההנחה
        reward += self.check_and_explode_rows(state) * 10  # נקודות לפי כמות הפיצוצים שקרו לאחר ההנחה
        return reward

    def count_squares_of_block(self, shape):
        return sum(sum(row) for row in shape)

    def print_block_squares(self, shape):
        count = self.count_squares_of_block(shape)
        print(f"Block has {count} squares")

    def count_ones_per_row_col(self, state: State):
        """
        Count how many occupied cells (non-zero) exist in each row and each
        column of the board, print the counts for every row and column, and
        return the counts.

        Args:
            state (State): The game state containing `Board` as a numpy array.

        Returns:
            tuple: (row_counts, col_counts) where each is a list of integers.
        """
        board = state.Board
        # Ensure board is a numpy array
        board_arr = np.array(board)

        # Count occupied cells (non-zero) per row and per column
        row_counts = np.sum(board_arr != 0, axis=1).tolist()
        col_counts = np.sum(board_arr != 0, axis=0).tolist()

        return row_counts, col_counts

    def sum_ones_in_affected_rows_cols(self, state: State, block: Block, position: tuple) -> int:
        """
        Sum the number of cells equal to 1 inside the bounding rows and columns
        where `block` is placed at `position`.

        Args:
            state (State): current game state with `Board` as a numpy array.
            block (Block): block object (or any with `shape` attribute).
            position (tuple): (grid_x, grid_y) top-left position on the board.

        Returns:
            int: total count of cells equal to 1 within the rectangle spanned by
                 the placed shape (rows x columns).
        """
        # Use count_ones_per_row_col to get per-row and per-column counts,
        # then sum those counts for rows and columns that the shape spans.
        shape_arr = np.array(getattr(block, 'shape', []))
        if shape_arr.size == 0:
            return 0

        h, w = shape_arr.shape
        grid_x, grid_y = position

        # compute the row/column indices covered by the shape (clamped to board)
        board = np.array(state.Board)
        min_y = max(0, grid_y)
        min_x = max(0, grid_x)
        max_y = min(board.shape[0], grid_y + h)
        max_x = min(board.shape[1], grid_x + w)

        if min_y >= max_y or min_x >= max_x:
            return 0

        row_counts, col_counts = self.count_ones_per_row_col(state)

        # sum counts for affected rows and columns
        total_rows = sum(row_counts[r] for r in range(min_y, max_y) if 0 <= r < len(row_counts))
        total_cols = sum(col_counts[c] for c in range(min_x, max_x) if 0 <= c < len(col_counts))

        total = int(total_rows + total_cols)
        return total

    def is_valid_move(self, state: State, block: Block, position: tuple) -> bool:
        """
        Check if placing the block at the given position is a valid move.
        """
        board = state.Board
        grid_x, grid_y = position  # המיקום על הלוח (קואורדינטות רשת)

        # Support both Block and SimpleNamespace-like objects that carry a `shape` attribute
        shape = getattr(block, 'shape', None)
        if shape is None:
            return False

        # Convert shape to numpy array for fast, vectorized checks
        shape_arr = np.array(shape)
        h, w = shape_arr.shape

        # Quick boundary check: shape must fully fit inside the board at the given position
        if grid_x < 0 or grid_y < 0 or (grid_x + w) > board.shape[1] or (grid_y + h) > board.shape[0]:
            return False

        # Extract the corresponding board slice and check overlap by elementwise multiply.
        # If any product is non-zero then an occupied cell would overlap the shape -> invalid.
        board_slice = board[grid_y:grid_y + h, grid_x:grid_x + w]
        if np.any(board_slice * shape_arr != 0):
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

    def check_and_generate_blocks(self):
        """
        Check if there are no more blocks available and generate new ones if needed.
        """
        if not self.state.Blocks:  # אם אין בלוקים ברשימה
            self.set_random_block()

    def check_and_explode_rows(self, state: State):
        """
        Check for full rows or columns, explode them, and update the score.
        """
        board = state.Board
        rows_to_explode = [y for y in range(board.shape[0]) if all(board[y, :] != 0)] # use numpy for efficient row checking
        cols_to_explode = [x for x in range(board.shape[1]) if all(board[:, x] != 0)] # use numpy for efficient column checking

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
        return num_explosions

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

    def GetAllPossibleMoves(self, state: State):
        """
        החזר את כל המהלכים החוקיים על הלוח הנוכחי עבור כל הצורות האפשריות.
        """
        board = state.Board # מגדיר את הלוח הקיים 
        shapes = self.all_shapes() #יוצר רשימה של כל הצורות 
        legal_moves = [] # יוצר רשימה של כל המהלכים החוקיים 

        for name, shape in shapes.items(): # על כל צורה והשם שלה 
            shape_h = len(shape)
            shape_w = len(shape[0]) if shape_h > 0 else 0

            # עבור כל מיקום אפשרי שבו תיבת ה-bounding של הצורה נכנסת ללוח
            max_y = board.shape[0] - shape_h
            max_x = board.shape[1] - shape_w
            if max_y < 0 or max_x < 0:
                continue

            for y in range(0, max_y + 1):
                for x in range(0, max_x + 1):
                    dummy = SimpleNamespace(shape=shape)
                    # בדיקה חוקיות המהלך בעזרת is_valid_move שמתבססת על ה-shape
                    if self.is_valid_move(state, dummy, (x, y)):
                        legal_moves.append((name, shape, (x, y)))

        return tuple(legal_moves)

    def AfterState(self, state: State, moves):
        """
        קבל את כל המהלכים (כפי שמוחזרים מ-`GetAllPossibleMoves`) והחזר רשימה של
        כל ה-`State` הפוטנציאליים אשר היו מתקבלים אם השחקן היה מבצע כל מהלך.
        """
        resulting_states = []
        for mv in moves: # mv => (name, shape, (x, y))
            try:
                name, shape, pos = mv
            except Exception:
                continue
            x, y = pos

            # העתק עמוק של ה-State כדי לא לשנות את המקור
            new_state = copy.deepcopy(state)

            # אובייקט דמה המייצג בלוק לצורך הכנסת הצורה אל הלוח
            dummy_block = Block(shape, pygame.Rect(0, 0, 0, 0), 1)

            # עדכון הלוח לפי המהלך (זה יעדכן גם את new_state.score)
            self.fix_block_to_board(new_state, dummy_block, (x, y))

            # בדיקה ופיצוץ שורות/עמודות במידה וקיימות
            self.check_and_explode_rows(new_state)

            # אם אין בלוקים ב-new_state, צור חדשים (השתמש ב-set_random_block עם פרמטר)
            if not new_state.Blocks:
                self.set_random_block(new_state)

            resulting_states.append(new_state)

        return resulting_states
    
    def tensor_shape(self, shape):
        shape_T = torch.tensor(shape, dtype=torch.float32)
        return shape_T
    
    def GetAllAfterStates(self, state):
        all_moves = self.GetAllPossibleMoves(state)
        all_after_states = self.AfterState(state, all_moves)
        return tuple(all_after_states)
        