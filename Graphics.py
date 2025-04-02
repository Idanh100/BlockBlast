import pygame
from pygame.locals import *

class Graphics:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Block Blast Game")
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.DARK_BLUE = (35, 50, 95)  # Background
        self.DARKER_BLUE = (25, 35, 70)  # Grid background
        self.LIGHT_BLUE = (80, 100, 170)  # Accent
        self.RED = (220, 70, 70)
        self.YELLOW = (240, 200, 50)
        self.ORANGE = (240, 130, 50)
        self.HIGHLIGHT_COLOR = (100, 150, 255)  # Highlight color for cells
        self.INVALID_HIGHLIGHT = (150, 50, 50, 128)  # Red tint for invalid placements
        
        # Grid settings
        self.GRID_SIZE = 40
        self.GRID_MARGIN = 2
        self.GRID_ORIGIN_X = 40
        self.GRID_ORIGIN_Y = 150
        
        # Load fonts
        self.large_font = pygame.font.SysFont(None, 120)
        self.medium_font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 32)
        
        # Button dimensions
        self.button_width = 200
        self.button_height = 50
    
    def draw_menu(self):
        """
        Draw the main menu screen.
        
        Returns:
            dict: Dictionary of UI elements with their rects
        """
        # Fill background
        self.screen.fill(self.DARK_BLUE)
        
        # Draw game title
        title = self.large_font.render("Block Blast", True, self.WHITE)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 100))
        
        # Draw start button
        start_button = pygame.Rect(
            self.width // 2 - self.button_width // 2,
            300,
            self.button_width,
            self.button_height
        )
        pygame.draw.rect(self.screen, self.LIGHT_BLUE, start_button, border_radius=10)
        start_text = self.medium_font.render("Start Game", True, self.WHITE)
        self.screen.blit(start_text, (start_button.centerx - start_text.get_width() // 2, 
                                      start_button.centery - start_text.get_height() // 2))
        
        # Draw quit button
        quit_button = pygame.Rect(
            self.width // 2 - self.button_width // 2,
            380,
            self.button_width,
            self.button_height
        )
        pygame.draw.rect(self.screen, self.RED, quit_button, border_radius=10)
        quit_text = self.medium_font.render("Quit", True, self.WHITE)
        self.screen.blit(quit_text, (quit_button.centerx - quit_text.get_width() // 2, 
                                    quit_button.centery - quit_text.get_height() // 2))
        
        # Draw basic instructions
        instruction_text = self.small_font.render("Place blocks to complete rows or columns", True, self.WHITE)
        self.screen.blit(instruction_text, (self.width // 2 - instruction_text.get_width() // 2, 500))
        
        return {
            "start_button": start_button,
            "quit_button": quit_button
        }
    
    def draw_game(self, state, highlighted_cells=[], highlight_color=None):
        """
        Draw the main game screen.
        
        Args:
            state: The current game state
            highlighted_cells: List of grid cells to highlight (passed from HumanAgent)
            highlight_color: The base color for highlighted cells
            
        Returns:
            dict: Dictionary of UI elements with their rects
        """
        # Fill background
        self.screen.fill(self.DARK_BLUE)
        
        # Draw score
        score_text = self.large_font.render(f"{state.score}", True, self.WHITE)
        self.screen.blit(score_text, (self.width // 2 - score_text.get_width() // 2, 60))
        
        # Draw lines cleared
        lines_text = self.small_font.render(f"Lines: {state.lines_cleared}", True, self.WHITE)
        self.screen.blit(lines_text, (20, 20))
        
        # Draw settings icon (gear)
        settings_icon = pygame.Rect(self.width - 60, 20, 40, 40)
        pygame.draw.circle(self.screen, self.LIGHT_BLUE, settings_icon.center, 20)
        
        # Draw grid background
        grid_width_px = state.grid_width * self.GRID_SIZE
        grid_height_px = state.grid_height * self.GRID_SIZE
        grid_rect = pygame.Rect(self.GRID_ORIGIN_X, self.GRID_ORIGIN_Y, grid_width_px, grid_height_px)
        pygame.draw.rect(self.screen, self.DARKER_BLUE, grid_rect)
        
        # Draw grid lines
        for x in range(state.grid_width + 1):
            pygame.draw.line(self.screen, self.DARK_BLUE, 
                             (self.GRID_ORIGIN_X + x * self.GRID_SIZE, self.GRID_ORIGIN_Y),
                             (self.GRID_ORIGIN_X + x * self.GRID_SIZE, self.GRID_ORIGIN_Y + grid_height_px), 2)
        
        for y in range(state.grid_height + 1):
            pygame.draw.line(self.screen, self.DARK_BLUE, 
                             (self.GRID_ORIGIN_X, self.GRID_ORIGIN_Y + y * self.GRID_SIZE),
                             (self.GRID_ORIGIN_X + grid_width_px, self.GRID_ORIGIN_Y + y * self.GRID_SIZE), 2)
        
        # Highlight cells if any and if there's a valid highlight color
        if highlighted_cells and highlight_color:
            for cell in highlighted_cells:
                grid_x, grid_y = cell
                # Check if the cell is within valid grid bounds
                if 0 <= grid_x < state.grid_width and 0 <= grid_y < state.grid_height:
                    # Determine highlight color - lighter version of the block's color
                    r, g, b = highlight_color
                    cell_highlight_color = (min(r + 80, 255), min(g + 80, 255), min(b + 80, 255))
                    
                    highlight_rect = pygame.Rect(
                        self.GRID_ORIGIN_X + grid_x * self.GRID_SIZE + self.GRID_MARGIN,
                        self.GRID_ORIGIN_Y + grid_y * self.GRID_SIZE + self.GRID_MARGIN,
                        self.GRID_SIZE - 2 * self.GRID_MARGIN,
                        self.GRID_SIZE - 2 * self.GRID_MARGIN
                    )
                    pygame.draw.rect(self.screen, cell_highlight_color, highlight_rect, border_radius=5)

        # Draw grid cells
        for y in range(state.grid_height):
            for x in range(state.grid_width):
                color = state.grid[y][x]
                if color is not None:
                    cell_rect = pygame.Rect(
                        self.GRID_ORIGIN_X + x * self.GRID_SIZE + self.GRID_MARGIN,
                        self.GRID_ORIGIN_Y + y * self.GRID_SIZE + self.GRID_MARGIN,
                        self.GRID_SIZE - 2 * self.GRID_MARGIN,
                        self.GRID_SIZE - 2 * self.GRID_MARGIN
                    )
                    pygame.draw.rect(self.screen, color, cell_rect, border_radius=5)
        
        # Draw "Available Blocks" text - moved up slightly to make room for blocks
        blocks_text = self.small_font.render("Available Blocks:", True, self.WHITE)
        self.screen.blit(blocks_text, (20, 550))
        
        # Draw available blocks
        block_ui_elements = {}
        for i, block in enumerate(state.available_blocks):
            # Only draw blocks that haven't been placed (not None)
            if block is not None:
                # Draw blocks at their actual screen positions, not adjusted by grid
                self._draw_block_at_position(block)
                block_ui_elements[f"block_{i}"] = block.rect
        
        return {
            "settings_button": settings_icon,
            "blocks": block_ui_elements,
            "grid_origin": (self.GRID_ORIGIN_X, self.GRID_ORIGIN_Y),
            "grid_size": self.GRID_SIZE
        }
    
    def _draw_block(self, block):
        """
        Draw a single block on the screen, adjusted for grid position.
        Used for blocks that should appear on the grid.
        
        Args:
            block: The Block object to draw
        """
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
    
    def _draw_block_at_position(self, block):
        """
        Draw a single block at its actual screen position.
        Used for available blocks at the bottom of the screen.
        
        Args:
            block: The Block object to draw
        """
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
    
    def draw_game_over(self, score, stats):
        """
        Draw the game over screen.
        
        Args:
            score: The player's final score
            stats: Game statistics dictionary
            
        Returns:
            dict: Dictionary of UI elements with their rects
        """
        # Fill background
        self.screen.fill(self.DARK_BLUE)
        
        # Draw game over text
        gameover_text = self.large_font.render("Game Over", True, self.WHITE)
        self.screen.blit(gameover_text, (self.width // 2 - gameover_text.get_width() // 2, 100))
        
        # Draw score
        score_text = self.medium_font.render(f"Score: {score}", True, self.WHITE)
        self.screen.blit(score_text, (self.width // 2 - score_text.get_width() // 2, 200))
        
        # Draw statistics
        y_pos = 250
        for key, value in stats.items():
            stat_text = self.small_font.render(f"{key.replace('_', ' ').title()}: {value}", True, self.WHITE)
            self.screen.blit(stat_text, (self.width // 2 - stat_text.get_width() // 2, y_pos))
            y_pos += 40
        
        # Draw return to menu button
        menu_button = pygame.Rect(
            self.width // 2 - self.button_width // 2,
            400,
            self.button_width,
            self.button_height
        )
        pygame.draw.rect(self.screen, self.LIGHT_BLUE, menu_button, border_radius=10)
        menu_text = self.medium_font.render("Main Menu", True, self.WHITE)
        self.screen.blit(menu_text, (menu_button.centerx - menu_text.get_width() // 2, 
                                     menu_button.centery - menu_text.get_height() // 2))
        
        return {
            "menu_button": menu_button
        }