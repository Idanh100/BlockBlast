import pygame

class Graphics:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.GRID_ORIGIN_Y = height / 10
        self.GRID_SIZE = width / 30
        self.GRID_ORIGIN_X = (width / 2) - (self.GRID_SIZE * 4)
        self.GRID_MARGIN = 4

        self.screen = pygame.display.set_mode((width, height))
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
        self.screen.fill(self.DARK_BLUE)
        self._draw_grid(state)

    def _draw_grid(self, state):
        grid = state.Board  # <<< השתמש במצב מהאובייקט State
        grid_height, grid_width = grid.shape

        grid_width_px = grid_width * self.GRID_SIZE
        grid_height_px = grid_height * self.GRID_SIZE
        grid_rect = pygame.Rect(self.GRID_ORIGIN_X, self.GRID_ORIGIN_Y, grid_width_px, grid_height_px)
        pygame.draw.rect(self.screen, self.DARKER_BLUE, grid_rect)
        
        # Draw grid lines
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
        for y in range(block.height):
            for x in range(block.width):
                if block.shape[y][x] == 1:
                    rect = pygame.Rect(
                        block.rect.x + x * self.GRID_SIZE + self.GRID_MARGIN,
                        block.rect.y + y * self.GRID_SIZE + self.GRID_MARGIN,
                        self.GRID_SIZE - 2 * self.GRID_MARGIN,
                        self.GRID_SIZE - 2 * self.GRID_MARGIN
                    )
                    pygame.draw.rect(self.screen, block.color, rect, border_radius=5)
