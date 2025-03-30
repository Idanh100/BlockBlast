Graphics.py
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
        # Fill background
        self.screen.fill(self.DARK_BLUE)
        
        # Draw game title
        title = self.large_font.render("Block Blast", True, self.WHITE)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 100))
        
        # Draw start button
        start_button = self._draw_button(self.width // 2, 300, "Start Game", self.LIGHT_BLUE)
        
        # Draw quit button
        quit_button = self._draw_button(self.width // 2, 380, "Quit", self.RED)
        
        return {
            "start_button": start_button,
            "quit_button": quit_button
        }
    
    def draw_game(self, state):
        # Fill background
        self.screen.fill(self.DARK_BLUE)
        
        # Draw score
        score_text = self.large_font.render(f"{state.score}", True, self.WHITE)
        self.screen.blit(score_text, (self.width // 2 - score_text.get_width() // 2, 60))
        
        # Draw settings icon (gear)
        settings_icon = pygame.Rect(self.width - 60, 20, 40, 40)
        pygame.draw.circle(self.screen, self.LIGHT_BLUE, settings_icon.center, 20)
        
        # Draw grid
        self._draw_grid(state)
        
        # Draw available blocks
        block_ui_elements = {}
        for i, block in enumerate(state.available_blocks):
            self._draw_block(block)
            block_ui_elements[f"block_{i}"] = block.rect
        
        return {
            "settings_button": settings_icon,
            "blocks": block_ui_elements,
            "grid_origin": (self.GRID_ORIGIN_X, self.GRID_ORIGIN_Y),
            "grid_size": self.GRID_SIZE
        }
    
    def _draw_button(self, x, y, text, color):
        button_rect = pygame.Rect(
            x - self.button_width // 2,
            y,
            self.button_width,
            self.button_height
        )
        pygame.draw.rect(self.screen, color, button_rect, border_radius=10)
        button_text = self.medium_font.render(text, True, self.WHITE)
        self.screen.blit(button_text, (button_rect.centerx - button_text.get_width() // 2, 
                                      button_rect.centery - button_text.get_height() // 2))
        return button_rect
    
    def _draw_grid(self, state):
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
    
    def _draw_block(self, block):
        for y in range(block.height):
            for x in range(block.width):
                if block.shape[y][x] == 1:
                    rect = pygame.Rect(
                        block.rect.x + x * self.GRID_SIZE,
                        block.rect.y + y * self.GRID_SIZE,
                        self.GRID_SIZE - self.GRID_MARGIN,
                        self.GRID_SIZE - self.GRID_MARGIN
                    )
                    pygame.draw.rect(self.screen, block.color, rect, border_radius=5)
    
    def draw_game_over(self, final_score, stats):
        # Fill background with overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Draw game over text
        game_over_text = self.large_font.render("GAME OVER", True, self.WHITE)
        self.screen.blit(game_over_text, 
                       (self.width // 2 - game_over_text.get_width() // 2, 150))
        
        # Draw final score
        score_text = self.medium_font.render(f"Your Score: {final_score}", True, self.WHITE)
        self.screen.blit(score_text, 
                       (self.width // 2 - score_text.get_width() // 2, 250))
        
        # Draw statistics
        y_pos = 320
        stats_texts = [
            f"Highest Score: {stats['highest_score']}",
            f"Average Score: {stats['avg_score']}",
            f"Games Played: {stats['games_played']}"
        ]
        
        for text in stats_texts:
            stat_text = self.small_font.render(text, True, self.WHITE)
            self.screen.blit(stat_text, 
                           (self.width // 2 - stat_text.get_width() // 2, y_pos))
            y_pos += 40
        
        # Draw back to menu button
        menu_button = self._draw_button(self.width // 2, 450, "Back to Menu", self.LIGHT_BLUE)
        
        return {
            "menu_button": menu_button
        }