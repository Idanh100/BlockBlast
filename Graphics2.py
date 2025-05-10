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
           
    def draw_game(self, state):
        """
        Draw the entire game state, including the board, blocks, and score.
        """
        self.screen.fill(self.DARK_BLUE)
        self._draw_grid(state)
        for block in state.Blocks:
            self._draw_block(block)
        
        # ציור הניקוד בצד שמאל במרכז
        self._draw_score(state.score)

    def _draw_grid(self, state):
        """
        Draw the game grid, including the blocks that have been fixed to the board.
        """
        grid = state.Board  # הלוח הנוכחי
        grid_height, grid_width = grid.shape

        grid_width_px = grid_width * self.GRID_SIZE
        grid_height_px = grid_height * self.GRID_SIZE
        grid_rect = pygame.Rect(self.GRID_ORIGIN_X, self.GRID_ORIGIN_Y, grid_width_px, grid_height_px)
        pygame.draw.rect(self.screen, self.DARKER_BLUE, grid_rect)  # רקע הלוח

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
