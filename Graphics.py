import pygame
from pygame.locals import *

class Graphics:
    def __init__(self, width, height):
        # Set to specific dimensions of 1920x1080
        self.width, self.height = 1920, 1080
        
        # Create a fullscreen window at the specified resolution
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Block Blast Game")
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.DARK_BLUE = (35, 50, 95)
        self.DARKER_BLUE = (25, 35, 70)
        self.LIGHT_BLUE = (80, 100, 170)
        self.RED = (220, 70, 70)
        self.YELLOW = (240, 200, 50)
        self.ORANGE = (240, 130, 50)
        self.HIGHLIGHT_COLOR = (100, 150, 255)
        self.INVALID_HIGHLIGHT = (150, 50, 50, 128)
        self.COMPLETE_LINE_HIGHLIGHT = (120, 240, 120, 160)
        self.GOLD_COLOR = (255, 215, 0)
        
        # Adjust grid settings for 1920x1080
        self.GRID_SIZE = 60  # Larger grid cells for better visibility and interaction
        self.GRID_MARGIN = int(self.GRID_SIZE * 0.05)
        
        # Center the grid horizontally
        self.GRID_ORIGIN_X = (self.width - (8 * self.GRID_SIZE)) // 2
        self.GRID_ORIGIN_Y = int(self.height * 0.2)
        
        # Load fonts with scaled sizes for 1920x1080
        self.large_font = pygame.font.SysFont(None, int(self.height * 0.14))
        self.medium_font = pygame.font.SysFont(None, int(self.height * 0.06))
        self.small_font = pygame.font.SysFont(None, int(self.height * 0.04))
        
        # Scale button dimensions
        self.button_width = int(self.width * 0.25)
        self.button_height = int(self.height * 0.06)
    
    def draw_menu(self):
        """Draw the main menu screen."""
        self.screen.fill(self.DARK_BLUE)
        
        # Draw game title
        title = self.large_font.render("Block Blast", True, self.WHITE)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, int(self.height * 0.13)))
        
        # Draw buttons
        start_button = pygame.Rect(self.width // 2 - self.button_width // 2, 
                                  int(self.height * 0.4), 
                                  self.button_width, self.button_height)
        quit_button = pygame.Rect(self.width // 2 - self.button_width // 2, 
                                int(self.height * 0.51), 
                                self.button_width, self.button_height)
        
        pygame.draw.rect(self.screen, self.LIGHT_BLUE, start_button, border_radius=10)
        pygame.draw.rect(self.screen, self.RED, quit_button, border_radius=10)
        
        # Draw button text
        start_text = self.medium_font.render("Start Game", True, self.WHITE)
        quit_text = self.medium_font.render("Quit", True, self.WHITE)
        
        self.screen.blit(start_text, (start_button.centerx - start_text.get_width() // 2, 
                                      start_button.centery - start_text.get_height() // 2))
        self.screen.blit(quit_text, (quit_button.centerx - quit_text.get_width() // 2, 
                                    quit_button.centery - quit_text.get_height() // 2))
        
        # Draw instructions
        instruction_text = self.small_font.render("Place blocks to complete rows or columns", True, self.WHITE)
        self.screen.blit(instruction_text, (self.width // 2 - instruction_text.get_width() // 2, 
                                           int(self.height * 0.67)))
        
        return {"start_button": start_button, "quit_button": quit_button}
    
    def draw_game(self, state, highlighted_cells=[], highlight_color=None):
        """Draw the main game screen."""
        self.screen.fill(self.DARK_BLUE)
        
        # Draw score and stats
        score_text = self.large_font.render(f"{state.score}", True, self.WHITE)
        lines_text = self.small_font.render(f"Lines: {state.lines_cleared}", True, self.WHITE)
        self.screen.blit(score_text, (self.width // 2 - score_text.get_width() // 2, int(self.height * 0.08)))
        self.screen.blit(lines_text, (int(self.width * 0.05), int(self.height * 0.03)))
        
        # Draw settings icon
        settings_icon = pygame.Rect(self.width - int(self.width * 0.1), int(self.height * 0.03), 
                                   int(self.width * 0.07), int(self.width * 0.07))
        pygame.draw.circle(self.screen, self.LIGHT_BLUE, settings_icon.center, int(self.width * 0.035))
        
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
        
        # Get completable rows and columns
        complete_rows = getattr(getattr(state, 'human_agent', None), 'complete_rows', [])
        complete_cols = getattr(getattr(state, 'human_agent', None), 'complete_cols', [])
        
        # Highlight cells
        if highlighted_cells and highlight_color:
            for cell in highlighted_cells:
                grid_x, grid_y = cell
                if 0 <= grid_x < state.grid_width and 0 <= grid_y < state.grid_height:
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
                    pygame.draw.rect(self.screen, 
                                    self.GOLD_COLOR if y in complete_rows or x in complete_cols else color, 
                                    cell_rect, border_radius=5)
        
        # Adjust position for blocks at the bottom - more space between blocks for larger screen
        blocks_y = int(self.height * 0.8)
        
        # Draw "Available Blocks" text
        blocks_text = self.small_font.render("Available Blocks:", True, self.WHITE)
        self.screen.blit(blocks_text, (int(self.width * 0.05), blocks_y - int(self.height * 0.05)))
        
        # Update block positions with wider spacing for 1920x1080
        block_positions = [
            int(self.width * 0.2), 
            int(self.width * 0.5), 
            int(self.width * 0.8)
        ]
        
        # Draw available blocks
        block_ui_elements = {}
        for i, block in enumerate(state.available_blocks):
            if block is not None:
                # Update block position if it's not being dragged
                if not (hasattr(state, 'human_agent') and state.human_agent.dragging_block == block):
                    block.rect.x = block_positions[i] - (block.width * self.GRID_SIZE // 2)
                    block.rect.y = blocks_y
                
                self._draw_block_at_position(block)
                
                # Create proper rect for the entire block surface area
                block_width = block.width * self.GRID_SIZE
                block_height = block.height * self.GRID_SIZE
                block_ui_elements[f"block_{i}"] = pygame.Rect(block.rect.x, block.rect.y, block_width, block_height)
        
        # Draw the currently dragged block on top of everything
        if hasattr(state, 'human_agent') and state.human_agent.dragging_block:
            self._draw_block_at_position(state.human_agent.dragging_block)
        
        return {
            "settings_button": settings_icon,
            "blocks": block_ui_elements,
            "grid_origin": (self.GRID_ORIGIN_X, self.GRID_ORIGIN_Y),
            "grid_size": self.GRID_SIZE
        }
    
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
    
    def _draw_block_at_position(self, block):
        """Draw a single block at its actual screen position."""
        self._draw_block(block)  # Reuse code since functionality is identical
    
    def draw_game_over(self, score, stats):
        """Draw the game over screen."""
        self.screen.fill(self.DARK_BLUE)
        
        # Draw game over text and score
        gameover_text = self.large_font.render("Game Over", True, self.WHITE)
        score_text = self.medium_font.render(f"Score: {score}", True, self.WHITE)
        
        self.screen.blit(gameover_text, (self.width // 2 - gameover_text.get_width() // 2, int(self.height * 0.13)))
        self.screen.blit(score_text, (self.width // 2 - score_text.get_width() // 2, int(self.height * 0.27)))
        
        # Draw statistics
        y_pos = int(self.height * 0.33)
        for key, value in stats.items():
            stat_text = self.small_font.render(f"{key.replace('_', ' ').title()}: {value}", True, self.WHITE)
            self.screen.blit(stat_text, (self.width // 2 - stat_text.get_width() // 2, y_pos))
            y_pos += int(self.height * 0.053)
        
        # Draw return to menu button
        menu_button = pygame.Rect(
            self.width // 2 - self.button_width // 2,
            int(self.height * 0.53),
            self.button_width,
            self.button_height
        )
        pygame.draw.rect(self.screen, self.LIGHT_BLUE, menu_button, border_radius=10)
        menu_text = self.medium_font.render("Main Menu", True, self.WHITE)
        self.screen.blit(menu_text, (menu_button.centerx - menu_text.get_width() // 2, 
                                     menu_button.centery - menu_text.get_height() // 2))
        
        return {"menu_button": menu_button}