import pygame

class Graphics:
    def __init__(self):
        pygame.init()
        info = pygame.display.get_desktop_sizes()[0]  # אם יש כמה מסכים – לוקח את הראשון
        self.width, self.height = info

        self.GRID_ORIGIN_Y = self.height / 10
        self.GRID_SIZE = self.width / 30
        self.GRID_ORIGIN_X = (self.width / 2) - (self.GRID_SIZE * 4)
        self.GRID_MARGIN = 4

        self.clock = pygame.time.Clock()
        self.clock.tick(60)  # מגביל ל־60 FPS

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Block Blast Game")

        self.WHITE = (255, 255, 255)
        self.DARK_BLUE = (35, 50, 95)  # Background
        self.DARKER_BLUE = (25, 35, 70)  # Grid background
        self.LIGHT_BLUE = (80, 100, 170)  # Accent
        self.RED = (220, 70, 70)
        self.YELLOW = (240, 200, 50)
        self.ORANGE = (240, 130, 50)
        self.GREEN = (100, 200, 100)
        self.BLUE = (100, 100, 240)
        self.PURPLE = (180, 100, 240)
        self.HIGHLIGHT_COLOR = (100, 150, 255)
        self.INVALID_HIGHLIGHT = (150, 50, 50, 128)
        self.COMPLETE_LINE_HIGHLIGHT = (120, 240, 120, 160)
        self.GOLD_COLOR = (255, 215, 0)
           
    def draw_game(self, state, dragging_block=None):
        """
        Draw the entire game state, including the board, blocks, and score.
        If a block is being dragged, highlight the potential placement.
        """
        self.screen.fill(self.DARK_BLUE)
        self._draw_grid(state, dragging_block)
        for block in state.Blocks:
            self._draw_block(block)
        
        # הדגשת שורות ועמודות שיתמלאו אם הבלוק יונח
        if dragging_block:
            self._highlight_full_lines(state, dragging_block)
        
        # ציור הניקוד בצד שמאל במרכז
        self._draw_score(state.score)

    def _draw_grid(self, state, dragging_block=None):
        """
        Draw the game grid, including the blocks that have been fixed to the board.
        If a block is being dragged, highlight the potential placement.
        """
        grid = state.Board  # הלוח הנוכחי
        grid_height, grid_width = grid.shape

        grid_width_px = grid_width * self.GRID_SIZE
        grid_height_px = grid_height * self.GRID_SIZE
        grid_rect = pygame.Rect(self.GRID_ORIGIN_X, self.GRID_ORIGIN_Y, grid_width_px, grid_height_px)
        pygame.draw.rect(self.screen, self.DARKER_BLUE, grid_rect)  # רקע הלוח

        # Highlight potential placement if dragging a block
        if dragging_block:
            self._highlight_potential_placement(state, dragging_block)

        # ציור המשבצות בלוח
        for y in range(grid_height):
            for x in range(grid_width):
                cell_value = grid[y][x]
                if cell_value != 0:  # אם התא אינו ריק
                    color = self.get_color_from_id(cell_value)  # קבלת הצבע לפי מזהה
                    rect = pygame.Rect(
                        self.GRID_ORIGIN_X + x * self.GRID_SIZE + self.GRID_MARGIN,
                        self.GRID_ORIGIN_Y + y * self.GRID_SIZE + self.GRID_MARGIN,
                        self.GRID_SIZE - 1.5 * self.GRID_MARGIN,
                        self.GRID_SIZE - 1.5 * self.GRID_MARGIN
                    )
                    # ציור התא בצבע המתאים עם קצוות מעוגלות
                    pygame.draw.rect(self.screen, color, rect, border_radius=5)
                    # ציור מסגרת התא עם קצוות מעוגלות
                    pygame.draw.rect(self.screen, self.DARK_BLUE, rect, width=2, border_radius=5)

        # ציור קווי הרשת
        for x in range(grid_width + 1):
            pygame.draw.line(self.screen, self.DARK_BLUE,
                             (self.GRID_ORIGIN_X + x * self.GRID_SIZE, self.GRID_ORIGIN_Y),
                             (self.GRID_ORIGIN_X + x * self.GRID_SIZE, self.GRID_ORIGIN_Y + grid_height_px), 2)

        for y in range(grid_height + 1):
            pygame.draw.line(self.screen, self.DARK_BLUE,
                             (self.GRID_ORIGIN_X, self.GRID_ORIGIN_Y + y * self.GRID_SIZE),
                             (self.GRID_ORIGIN_X + grid_width_px, self.GRID_ORIGIN_Y + y * self.GRID_SIZE), 2)
            
    def _draw_block(self, block):
        """Draw a single block on the screen, adjusted for grid position."""
        for y in range(len(block.shape)):
            for x in range(len(block.shape[0])):
                if block.shape[y][x] == 1:
                    rect = pygame.Rect(
                        block.rect.x + x * self.GRID_SIZE + self.GRID_MARGIN,
                        block.rect.y + y * self.GRID_SIZE + self.GRID_MARGIN,
                        self.GRID_SIZE - 2 * self.GRID_MARGIN,
                        self.GRID_SIZE - 2 * self.GRID_MARGIN
                    )
                    pygame.draw.rect(self.screen, block.color, rect, border_radius=5)

    def get_color_from_id(self, color_id):
        """
        Get the color corresponding to a given color ID.

        Args:
            color_id (int or float): The color ID.

        Returns:
            tuple: The RGB color.
        """
        colors = [
            (220, 70, 70),    # RED
            (240, 200, 50),   # YELLOW
            (240, 130, 50),   # ORANGE
            (100, 200, 100),  # GREEN
            (100, 100, 240),  # BLUE
            (180, 100, 240)   # PURPLE
        ]
        return colors[(int(color_id)) % len(colors)]  # המרת color_id ל-int

    def _draw_score(self, score):
        """
        Draw the score at the top-left corner of the screen, aligned with the top of the grid,
        and centered between the left edge of the screen and the left edge of the grid.
        """
        font = pygame.font.SysFont("Arial", 48, bold=True)  # גופן גדול ובולט
        score_text = font.render(f"Score: {score}", True, self.WHITE)
        text_rect = score_text.get_rect()

        # חישוב המיקום: מרכז בין הקצה השמאלי של המסך לקצה השמאלי של הלוח
        center_x = self.GRID_ORIGIN_X / 2
        text_rect.midtop = (center_x, self.GRID_ORIGIN_Y)  # מיקום בגובה הקצה העליון של הלוח

        # רקע לניקוד
        background_rect = pygame.Rect(
            text_rect.x - 10, text_rect.y - 10,
            text_rect.width + 20, text_rect.height + 20
        )
        pygame.draw.rect(self.screen, self.LIGHT_BLUE, background_rect, border_radius=15)

        # מסגרת מסביב לרקע
        pygame.draw.rect(self.screen, self.GOLD_COLOR, background_rect, width=3, border_radius=15)

        # ציור הטקסט
        self.screen.blit(score_text, text_rect)

    def draw_game_over(self, state):
        """
        Draw the Game Over screen with the final score and other details.

        Args:
            state (State): The current game state.
        """
        self.screen.fill(self.DARK_BLUE)

        font = pygame.font.SysFont("Arial", 72, bold=True)
        game_over_text = font.render("Game Over", True, self.RED)
        text_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 3))
        self.screen.blit(game_over_text, text_rect)

        font = pygame.font.SysFont("Arial", 48)
        score_text = font.render(f"Final Score: {state.score}", True, self.WHITE)
        score_rect = score_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(score_text, score_rect)

        font = pygame.font.SysFont("Arial", 36)
        restart_text = font.render("Press R to Restart or Q to Quit", True, self.YELLOW)
        restart_rect = restart_text.get_rect(center=(self.width // 2, self.height // 1.5))
        self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def _highlight_potential_placement(self, state, block):
        """
        Highlight the potential placement of the block on the grid if the move is valid.
        """
        grid_x = int((block.rect.x - self.GRID_ORIGIN_X) / self.GRID_SIZE)
        grid_y = int((block.rect.y - self.GRID_ORIGIN_Y) / self.GRID_SIZE)

        # בדיקת חוקיות המהלך
        if not self._is_valid_move(state, block, (grid_x, grid_y)):
            return  # אם המהלך אינו חוקי, לא מציירים הארה

        # יצירת עותק זמני של הלוח
        temp_board = state.Board.copy()
        for y, row in enumerate(block.shape):
            for x, cell in enumerate(row):
                if cell == 1:  # תא פעיל בבלוק
                    board_x = grid_x + x
                    board_y = grid_y + y
                    if 0 <= board_x < temp_board.shape[1] and 0 <= board_y < temp_board.shape[0]:
                        temp_board[board_y][board_x] = 1  # סימון התא כאילו הבלוק הונח

        # בדיקת שורות ועמודות מלאות
        rows_to_highlight = [y for y in range(temp_board.shape[0]) if all(temp_board[y, :] != 0)]
        cols_to_highlight = [x for x in range(temp_board.shape[1]) if all(temp_board[:, x] != 0)]

        # הארה של המיקום הפוטנציאלי של הבלוק
        for y, row in enumerate(block.shape):
            for x, cell in enumerate(row):
                if cell == 1:  # תא פעיל בבלוק
                    board_x = grid_x + x
                    board_y = grid_y + y

                    # בדיקה אם התא בתוך גבולות הלוח
                    if 0 <= board_x < state.Board.shape[1] and 0 <= board_y < state.Board.shape[0]:
                        # בדיקה אם התא שייך לשורה או עמודה שתתפוצץ
                        if board_y in rows_to_highlight or board_x in cols_to_highlight:
                            color = self.GOLD_COLOR  # צבע זהב
                        else:
                            color = tuple(min(c + 50, 255) for c in block.color)  # צבע בהיר יותר

                        rect = pygame.Rect(
                            self.GRID_ORIGIN_X + board_x * self.GRID_SIZE + self.GRID_MARGIN,
                            self.GRID_ORIGIN_Y + board_y * self.GRID_SIZE + self.GRID_MARGIN,
                            self.GRID_SIZE - 1.5 * self.GRID_MARGIN,
                            self.GRID_SIZE - 1.5 * self.GRID_MARGIN
                        )
                        pygame.draw.rect(self.screen, color, rect, border_radius=5)

    def _is_valid_move(self, state, block, position):
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
        grid_x, grid_y = position

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

    def _highlight_full_lines(self, state, block):
        """
        Highlight the blocks in rows and columns that will become full if the block is placed,
        including the blocks the user is about to place.
        """
        grid_x = int((block.rect.x - self.GRID_ORIGIN_X) / self.GRID_SIZE)
        grid_y = int((block.rect.y - self.GRID_ORIGIN_Y) / self.GRID_SIZE)

        # בדיקת חוקיות המהלך
        if not self._is_valid_move(state, block, (grid_x, grid_y)):
            return  # אם המהלך אינו חוקי, לא מציירים כלום

        # יצירת עותק זמני של הלוח
        temp_board = state.Board.copy()
        for y, row in enumerate(block.shape):
            for x, cell in enumerate(row):
                if cell == 1:  # תא פעיל בבלוק
                    board_x = grid_x + x
                    board_y = grid_y + y
                    if 0 <= board_x < temp_board.shape[1] and 0 <= board_y < temp_board.shape[0]:
                        temp_board[board_y][board_x] = 1  # סימון התא כאילו הבלוק הונח

        # בדיקת שורות ועמודות מלאות
        rows_to_highlight = [y for y in range(temp_board.shape[0]) if all(temp_board[y, :] != 0)]
        cols_to_highlight = [x for x in range(temp_board.shape[1]) if all(temp_board[:, x] != 0)]

        # הדגשת הבלוקים המונחים בשורות מלאות
        for row in rows_to_highlight:
            for col in range(temp_board.shape[1]):
                if state.Board[row, col] != 0 or any(
                    cell == 1 and grid_x + x == col and grid_y + y == row
                    for y, row_cells in enumerate(block.shape)
                    for x, cell in enumerate(row_cells)
                ):  # אם יש בלוק מונח או בלוק פוטנציאלי
                    rect = pygame.Rect(
                        self.GRID_ORIGIN_X + col * self.GRID_SIZE + self.GRID_MARGIN,
                        self.GRID_ORIGIN_Y + row * self.GRID_SIZE + self.GRID_MARGIN,
                        self.GRID_SIZE - 1.5 * self.GRID_MARGIN,
                        self.GRID_SIZE - 1.5 * self.GRID_MARGIN
                    )
                    pygame.draw.rect(self.screen, self.GOLD_COLOR, rect, border_radius=5)

        # הדגשת הבלוקים המונחים בעמודות מלאות
        for col in cols_to_highlight:
            for row in range(temp_board.shape[0]):
                if state.Board[row, col] != 0 or any(
                    cell == 1 and grid_x + x == col and grid_y + y == row
                    for y, row_cells in enumerate(block.shape)
                    for x, cell in enumerate(row_cells)
                ):  # אם יש בלוק מונח או בלוק פוטנציאלי
                    rect = pygame.Rect(
                        self.GRID_ORIGIN_X + col * self.GRID_SIZE + self.GRID_MARGIN,
                        self.GRID_ORIGIN_Y + row * self.GRID_SIZE + self.GRID_MARGIN,
                        self.GRID_SIZE - 1.5 * self.GRID_MARGIN,
                        self.GRID_SIZE - 1.5 * self.GRID_MARGIN
                    )
                    pygame.draw.rect(self.screen, self.GOLD_COLOR, rect, border_radius=5)
