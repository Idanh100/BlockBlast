import pygame
import random
from CONSTANTS import *

class Graphics:
    def __init__(self):
        pygame.init()
        info = pygame.display.get_desktop_sizes()[0]
        self.width, self.height = info

        self.GRID_ORIGIN_Y = self.height / 10
        self.GRID_SIZE = self.width / 30
        self.GRID_ORIGIN_X = (self.width / 2) - (self.GRID_SIZE * 4)
        self.GRID_MARGIN = GRID_MARGIN

        self.clock = pygame.time.Clock()
        self.clock.tick(FPS)

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Block Blast Game")

        self.frame_count = 0
        self.background_blocks = []
        
        from Environment2 import Environment
        from State2 import State
        self.env = Environment(State())

    def draw_game(self, state, dragging_block=None):
        self.screen.fill(COLOR_DARK_BLUE)
        self._draw_grid(state, dragging_block)
        for block in state.Blocks:
            self._draw_block(block)
        
        if dragging_block:
            self._highlight_full_lines(state, dragging_block)
        
        self._draw_score(state.score)

        self._draw_combo_animation(state)
        
        close_button_rect = self._draw_close_button()
        
        return close_button_rect

    def _draw_grid(self, state, dragging_block=None):
        grid = state.Board
        grid_height, grid_width = grid.shape

        grid_width_px = grid_width * self.GRID_SIZE
        grid_height_px = grid_height * self.GRID_SIZE
        grid_rect = pygame.Rect(self.GRID_ORIGIN_X, self.GRID_ORIGIN_Y, grid_width_px, grid_height_px)
        pygame.draw.rect(self.screen, COLOR_DARKER_BLUE, grid_rect)

        if dragging_block:
            self._highlight_potential_placement(state, dragging_block)

        for y in range(grid_height):
            for x in range(grid_width):
                cell_value = grid[y][x]
                if cell_value != 0:
                    color = self.get_color_from_id(cell_value)
                    rect = pygame.Rect(
                        self.GRID_ORIGIN_X + x * self.GRID_SIZE + self.GRID_MARGIN,
                        self.GRID_ORIGIN_Y + y * self.GRID_SIZE + self.GRID_MARGIN,
                        self.GRID_SIZE - 1.5 * self.GRID_MARGIN,
                        self.GRID_SIZE - 1.5 * self.GRID_MARGIN
                    )
                    pygame.draw.rect(self.screen, color, rect, border_radius=5)
                    pygame.draw.rect(self.screen, COLOR_DARK_BLUE, rect, width=2, border_radius=5)

        for x in range(grid_width + 1):
            pygame.draw.line(self.screen, COLOR_DARK_BLUE,
                             (self.GRID_ORIGIN_X + x * self.GRID_SIZE, self.GRID_ORIGIN_Y),
                             (self.GRID_ORIGIN_X + x * self.GRID_SIZE, self.GRID_ORIGIN_Y + grid_height_px), 2)

        for y in range(grid_height + 1):
            pygame.draw.line(self.screen, COLOR_DARK_BLUE,
                             (self.GRID_ORIGIN_X, self.GRID_ORIGIN_Y + y * self.GRID_SIZE),
                             (self.GRID_ORIGIN_X + grid_width_px, self.GRID_ORIGIN_Y + y * self.GRID_SIZE), 2)
            
    def _draw_block(self, block):
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
        colors = [
            (220, 70, 70),    # RED
            (240, 200, 50),   # YELLOW
            (240, 130, 50),   # ORANGE
            (100, 200, 100),  # GREEN
            (100, 100, 240),  # BLUE
            (180, 100, 240)   # PURPLE
        ]
        return colors[(int(color_id)) % len(colors)]

    def _draw_score(self, score):
        font = pygame.font.SysFont("Arial", 48, bold=True)
        score_text = font.render(f"Score: {score}", True, COLOR_WHITE)
        text_rect = score_text.get_rect()

        grid_right_x = self.GRID_ORIGIN_X + self.GRID_SIZE * 8
        center_x = (grid_right_x + self.width) / 2
        text_rect.midtop = (center_x, self.GRID_ORIGIN_Y + 40)

        background_rect = pygame.Rect(
            text_rect.x - 20, text_rect.y - 20,
            text_rect.width + 40, text_rect.height + 40
        )
        pygame.draw.rect(self.screen, COLOR_DARKER_BLUE, background_rect, border_radius=15)

        pygame.draw.rect(self.screen, COLOR_GOLD, background_rect, width=5, border_radius=15)

        self.screen.blit(score_text, text_rect)

    def draw_game_over(self, state):
        self.screen.fill(COLOR_DARK_BLUE)
        self.frame_count += 1

        if self.frame_count % 60 == 0 or not self.background_blocks:
            self._generate_background_blocks()

        self.screen.fill(COLOR_DARK_BLUE)

        self. _draw_background_blocks()

        font = pygame.font.SysFont("Arial", 72, bold=True)
        game_over_text = font.render("Game Over", True, COLOR_RED)
        game_over_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 4))

        game_over_background = pygame.Rect(
            game_over_rect.x - 20, game_over_rect.y - 20,
            game_over_rect.width + 40, game_over_rect.height + 40
        )
        pygame.draw.rect(self.screen, COLOR_DARKER_BLUE, game_over_background, border_radius=15)
        pygame.draw.rect(self.screen, COLOR_GOLD, game_over_background, width=5, border_radius=15)
        self.screen.blit(game_over_text, game_over_rect)

        score_font = pygame.font.SysFont("Arial", 48, bold=True)
        score_text = score_font.render(f"Your Score: {state.score}", True, COLOR_WHITE)
        score_rect = score_text.get_rect(center=(self.width // 2, self.height // 4 + 100))

        score_background = pygame.Rect(
            score_rect.x - 20, score_rect.y - 20,
            score_rect.width + 40, score_rect.height + 40
        )
        pygame.draw.rect(self.screen, COLOR_DARKER_BLUE, score_background, border_radius=15)
        pygame.draw.rect(self.screen, COLOR_GOLD, score_background, width=5, border_radius=15)
        self.screen.blit(score_text, score_rect)

        mouse_x, mouse_y = pygame.mouse.get_pos()

        restart_button = pygame.Rect(self.width // 2 - 150, self.height // 2 - 50, 300, 70)
        restart_color = COLOR_GREEN if not restart_button.collidepoint(mouse_x, mouse_y) else (0, 200, 0)
        pygame.draw.rect(self.screen, restart_color, restart_button, border_radius=15)
        pygame.draw.rect(self.screen, COLOR_WHITE, restart_button, width=3, border_radius=15)
        restart_text = pygame.font.SysFont("Arial", 48).render("Restart", True, COLOR_WHITE)
        restart_text_rect = restart_text.get_rect(center=restart_button.center)
        self.screen.blit(restart_text, restart_text_rect)

        main_menu_button = pygame.Rect(self.width // 2 - 150, self.height // 2 + 50, 300, 70)
        main_menu_color = COLOR_BLUE if not main_menu_button.collidepoint(mouse_x, mouse_y) else (0, 0, 200)
        pygame.draw.rect(self.screen, main_menu_color, main_menu_button, border_radius=15)
        pygame.draw.rect(self.screen, COLOR_WHITE, main_menu_button, width=3, border_radius=15)
        main_menu_text = pygame.font.SysFont("Arial", 48).render("Main Menu", True, COLOR_WHITE)
        main_menu_text_rect = main_menu_text.get_rect(center=main_menu_button.center)
        self.screen.blit(main_menu_text, main_menu_text_rect)

        pygame.display.flip()

        return restart_button, main_menu_button

    def _highlight_potential_placement(self, state, block):
        grid_x = int((block.rect.x - self.GRID_ORIGIN_X) / self.GRID_SIZE)
        grid_y = int((block.rect.y - self.GRID_ORIGIN_Y) / self.GRID_SIZE)

        if not self.env.is_valid_move(state, block, (grid_x, grid_y)):
            return

        temp_board = state.Board.copy()
        for y, row in enumerate(block.shape):
            for x, cell in enumerate(row):
                if cell == 1:
                    board_x = grid_x + x
                    board_y = grid_y + y
                    if 0 <= board_x < temp_board.shape[1] and 0 <= board_y < temp_board.shape[0]:
                        temp_board[board_y][board_x] = 1

        rows_to_highlight = [y for y in range(temp_board.shape[0]) if all(temp_board[y, :] != 0)]
        cols_to_highlight = [x for x in range(temp_board.shape[1]) if all(temp_board[:, x] != 0)]

        for y, row in enumerate(block.shape):
            for x, cell in enumerate(row):
                if cell == 1:
                    board_x = grid_x + x
                    board_y = grid_y + y

                    if 0 <= board_x < state.Board.shape[1] and 0 <= board_y < state.Board.shape[0]:
                        color = tuple(min(c + 50, 255) for c in block.color)

                        rect = pygame.Rect(
                            self.GRID_ORIGIN_X + board_x * self.GRID_SIZE + self.GRID_MARGIN,
                            self.GRID_ORIGIN_Y + board_y * self.GRID_SIZE + self.GRID_MARGIN,
                            self.GRID_SIZE - 1.5 * self.GRID_MARGIN,
                            self.GRID_SIZE - 1.5 * self.GRID_MARGIN
                        )
                        pygame.draw.rect(self.screen, color, rect, border_radius=5)

    def _highlight_full_lines(self, state, block):
        grid_x = int((block.rect.x - self.GRID_ORIGIN_X) / self.GRID_SIZE)
        grid_y = int((block.rect.y - self.GRID_ORIGIN_Y) / self.GRID_SIZE)

        if not self.env.is_valid_move(state, block, (grid_x, grid_y)):
            return

        temp_board = state.Board.copy()
        for y, row in enumerate(block.shape):
            for x, cell in enumerate(row):
                if cell == 1:
                    board_x = grid_x + x
                    board_y = grid_y + y
                    if 0 <= board_x < temp_board.shape[1] and 0 <= board_y < temp_board.shape[0]:
                        temp_board[board_y][board_x] = 1

        rows_to_highlight = [y for y in range(temp_board.shape[0]) if all(temp_board[y, :] != 0)]
        cols_to_highlight = [x for x in range(temp_board.shape[1]) if all(temp_board[:, x] != 0)]

        for row in rows_to_highlight:
            for col in range(temp_board.shape[1]):
                if any(
                    cell == 1 and grid_x + x == col and grid_y + y == row
                    for y, row_cells in enumerate(block.shape)
                    for x, cell in enumerate(row_cells)
                ):
                    continue

                rect = pygame.Rect(
                    self.GRID_ORIGIN_X + col * self.GRID_SIZE + self.GRID_MARGIN,
                    self.GRID_ORIGIN_Y + row * self.GRID_SIZE + self.GRID_MARGIN,
                    self.GRID_SIZE - 1.5 * self.GRID_MARGIN,
                    self.GRID_SIZE - 1.5 * self.GRID_MARGIN
                )
                pygame.draw.rect(self.screen, self.GOLD_COLOR, rect, border_radius=5)

        for col in cols_to_highlight:
            for row in range(temp_board.shape[0]):
                if any(
                    cell == 1 and grid_x + x == col and grid_y + y == row
                    for y, row_cells in enumerate(block.shape)
                    for x, cell in enumerate(row_cells)
                ):
                    continue

                rect = pygame.Rect(
                    self.GRID_ORIGIN_X + col * self.GRID_SIZE + self.GRID_MARGIN,
                    self.GRID_ORIGIN_Y + row * self.GRID_SIZE + self.GRID_MARGIN,
                    self.GRID_SIZE - 1.5 * self.GRID_MARGIN,
                    self.GRID_SIZE - 1.5 * self.GRID_MARGIN
                )
                pygame.draw.rect(self.screen, self.GOLD_COLOR, rect, border_radius=5)

    def _draw_combo_animation(self, state):
        if state.in_combo and state.combo_count >= 2:
            font = pygame.font.SysFont("Arial", 36, bold=True)
            combo_text = font.render(f"Combo x{state.combo_count}!", True, COLOR_GOLD)
            text_rect = combo_text.get_rect()

            grid_right_x = self.GRID_ORIGIN_X + self.GRID_SIZE * 8
            center_x = (grid_right_x + self.width) / 2
            text_rect.midtop = (center_x, self.GRID_ORIGIN_Y + 120)

            background_rect = pygame.Rect(
                text_rect.x - 10, text_rect.y - 10,
                text_rect.width + 20, text_rect.height + 20
            )
            pygame.draw.rect(self.screen, COLOR_LIGHT_BLUE, background_rect, border_radius=15)

            pygame.draw.rect(self.screen, COLOR_GOLD, background_rect, width=3, border_radius=15)

            self.screen.blit(combo_text, text_rect)

    def draw_main_menu(self):
        self.frame_count += 1

        if self.frame_count % 60 == 0 or not self.background_blocks:
            self._generate_background_blocks()

        self.screen.fill(COLOR_DARK_BLUE)

        self. _draw_background_blocks()

        font = pygame.font.SysFont("Arial", 72, bold=True)
        title_text = font.render("Block Blast Game", True, COLOR_GOLD)
        title_rect = title_text.get_rect(center=(self.width // 2, self.height // 4))

        background_rect = pygame.Rect(
            title_rect.x - 20, title_rect.y - 20,
            title_rect.width + 40, title_rect.height + 40
        )
        pygame.draw.rect(self.screen, COLOR_DARKER_BLUE, background_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLOR_GOLD, background_rect, width=5, border_radius=15)
        self.screen.blit(title_text, title_rect)

        mouse_x, mouse_y = pygame.mouse.get_pos()

        play_button = pygame.Rect(self.width // 2 - 150, self.height // 2 - 100, 300, 70)
        play_color = COLOR_GREEN if not play_button.collidepoint(mouse_x, mouse_y) else (0, 200, 0)
        pygame.draw.rect(self.screen, play_color, play_button, border_radius=15)
        pygame.draw.rect(self.screen, COLOR_WHITE, play_button, width=3, border_radius=15)
        play_text = pygame.font.SysFont("Arial", 48).render("Play", True, COLOR_WHITE)
        play_text_rect = play_text.get_rect(center=play_button.center)
        self.screen.blit(play_text, play_text_rect)

        train_button = pygame.Rect(self.width // 2 - 150, self.height // 2, 300, 70)
        train_color = COLOR_BLUE if not train_button.collidepoint(mouse_x, mouse_y) else (0, 0, 200)
        pygame.draw.rect(self.screen, train_color, train_button, border_radius=15)
        pygame.draw.rect(self.screen, COLOR_WHITE, train_button, width=3, border_radius=15)
        train_text = pygame.font.SysFont("Arial", 48).render("AI Play", True, COLOR_WHITE)
        train_text_rect = train_text.get_rect(center=train_button.center)
        self.screen.blit(train_text, train_text_rect)

        quit_button = pygame.Rect(self.width // 2 - 150, self.height // 2 + 100, 300, 70)
        quit_color = COLOR_RED if not quit_button.collidepoint(mouse_x, mouse_y) else (200, 0, 0)
        pygame.draw.rect(self.screen, quit_color, quit_button, border_radius=15)
        pygame.draw.rect(self.screen, COLOR_WHITE, quit_button, width=3, border_radius=15)
        quit_text = pygame.font.SysFont("Arial", 48).render("Quit", True, COLOR_WHITE)
        quit_text_rect = quit_text.get_rect(center=quit_button.center)
        self.screen.blit(quit_text, quit_text_rect)

        pygame.display.flip()

        return play_button, train_button, quit_button

    def _generate_background_blocks(self):
        block_size = int(self.GRID_SIZE)
        spacing = int(self.GRID_SIZE * 3)
        colors = [COLOR_RED, COLOR_YELLOW, COLOR_ORANGE, COLOR_GREEN, COLOR_BLUE, COLOR_PURPLE]

        block_shapes = [
            [[1, 1], [1, 1]],
            [[1, 1, 1], [0, 1, 0]],
            [[1, 1, 1, 1]],
            [[1, 0], [1, 0], [1, 1]],
            [[0, 1], [0, 1], [1, 1]]
        ]

        blocks = []
        for y in range(0, int(self.height), spacing):
            for x in range(0, int(self.width), spacing):
                shape = random.choice(block_shapes)
                color = random.choice(colors)
                blocks.append((shape, color, x, y))
        self.background_blocks = blocks

    def _draw_background_blocks(self):
        block_size = int(self.GRID_SIZE)
        for shape, color, x, y in self.background_blocks:
            for row_idx, row in enumerate(shape):
                for col_idx, cell in enumerate(row):
                    if cell == 1:
                        rect = pygame.Rect(
                            x + col_idx * block_size + self.GRID_MARGIN,
                            y + row_idx * block_size + self.GRID_MARGIN,
                            block_size - self.GRID_MARGIN,
                            block_size - self.GRID_MARGIN
                        )
                        pygame.draw.rect(self.screen, color, rect, border_radius=5)
    
    def _draw_close_button(self):
        button_size = 50
        button_x = 20
        button_y = 20
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
        
        is_hovering = button_rect.collidepoint(mouse_x, mouse_y)
        
        button_color = (255, 80, 80) if is_hovering else (220, 50, 50)
        
        pygame.draw.rect(self.screen, button_color, button_rect, border_radius=8)
        
        pygame.draw.rect(self.screen, COLOR_WHITE, button_rect, width=2, border_radius=8)
        
        line_length = 18
        center_x = button_x + button_size // 2
        center_y = button_y + button_size // 2
        
        pygame.draw.line(
            self.screen,
            COLOR_WHITE,
            (center_x - line_length, center_y - line_length),
            (center_x + line_length, center_y + line_length),
            width=3
        )
        pygame.draw.line(
            self.screen,
            COLOR_WHITE,
            (center_x + line_length, center_y - line_length),
            (center_x - line_length, center_y + line_length),
            width=3
        )
        
        return button_rect
    
    def get_close_button_rect(self):
        button_size = 50
        button_x = 20
        button_y = 20
        return pygame.Rect(button_x, button_y, button_size, button_size)
