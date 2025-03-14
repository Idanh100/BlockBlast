import pygame
import random

class Block:
    def __init__(self, shape, color, position):
        self.shape = shape
        self.color = color
        self.width = len(shape[0])
        self.height = len(shape)
        self.dragging = False
        self.rect = pygame.Rect(position[0], position[1], 
                               self.width * 40, 
                               self.height * 40)  # Using 40 as GRID_SIZE
    
    def can_place(self, grid, grid_x, grid_y, grid_width, grid_height):
        for y in range(self.height):
            for x in range(self.width):
                if self.shape[y][x] == 1:
                    # Check if position is valid
                    if grid_x + x < 0 or grid_x + x >= grid_width or grid_y + y < 0 or grid_y + y >= grid_height:
                        return False
                    # Check if cell is already occupied
                    if grid[grid_y + y][grid_x + x] is not None:
                        return False
        return True
    
    def place(self, grid, grid_x, grid_y):
        for y in range(self.height):
            for x in range(self.width):
                if self.shape[y][x] == 1:
                    grid[grid_y + y][grid_x + x] = self.color


class State:
    def __init__(self):
        self.reset()
    
    def reset(self):
        # Define colors
        self.RED = (220, 70, 70)
        self.YELLOW = (240, 200, 50)
        self.ORANGE = (240, 130, 50)
        
        # Grid dimensions
        self.grid_width = 8
        self.grid_height = 8
        self.grid = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # Game state
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        
        # Create initial blocks
        self.available_blocks = self.generate_initial_blocks()
    
    def generate_initial_blocks(self):
        blocks = []
        
        # Red 3x3 block (as seen in the screenshot)
        red_shape = [[1, 1, 1], 
                     [1, 1, 1], 
                     [1, 1, 1]]
        red_block = Block(red_shape, self.RED, (60, 600))
        blocks.append(red_block)
        
        # Yellow 1x5 block
        yellow_shape = [[1, 1, 1, 1, 1]]
        yellow_block = Block(yellow_shape, self.YELLOW, (170, 600))
        blocks.append(yellow_block)
        
        # Orange 1x5 block
        orange_shape = [[1, 1, 1, 1, 1]]
        orange_block = Block(orange_shape, self.ORANGE, (280, 600))
        blocks.append(orange_block)
        
        return blocks
    
    def generate_new_block(self, index):
        # Replace used block with a new one
        if index == 0:  # Red block slot
            shapes = [
                [[1, 1, 1], [1, 1, 1], [1, 1, 1]],  # 3x3
                [[1, 1], [1, 1]],  # 2x2
                [[1, 1, 1], [1, 1, 1]]  # 3x2
            ]
            shape = random.choice(shapes)
            return Block(shape, self.RED, (60, 600))
        elif index == 1:  # Yellow block slot
            shapes = [
                [[1, 1, 1, 1, 1]],  # 1x5
                [[1, 1, 1, 1]],  # 1x4
                [[1, 1, 1]]  # 1x3
            ]
            shape = random.choice(shapes)
            return Block(shape, self.YELLOW, (170, 600))
        else:  # Orange block slot
            shapes = [
                [[1, 1, 1, 1, 1]],  # 1x5
                [[1, 1, 1, 1]],  # 1x4
                [[1, 1, 1]]  # 1x3
            ]
            shape = random.choice(shapes)
            return Block(shape, self.ORANGE, (280, 600))
    
    def check_clear_lines(self):
        lines_cleared = 0
        
        # Check rows
        rows_to_clear = []
        for y in range(self.grid_height):
            if all(self.grid[y][x] is not None for x in range(self.grid_width)):
                rows_to_clear.append(y)
                lines_cleared += 1
        
        # Check columns
        cols_to_clear = []
        for x in range(self.grid_width):
            if all(self.grid[y][x] is not None for y in range(self.grid_height)):
                cols_to_clear.append(x)
                lines_cleared += 1
        
        # Clear rows
        for y in rows_to_clear:
            for x in range(self.grid_width):
                self.grid[y][x] = None
        
        # Clear columns
        for x in cols_to_clear:
            for y in range(self.grid_height):
                self.grid[y][x] = None
        
        # Update total lines cleared
        self.lines_cleared += lines_cleared
        
        return lines_cleared
    
    def can_place_any_block(self):
        for block in self.available_blocks:
            for y in range(self.grid_height - block.height + 1):
                for x in range(self.grid_width - block.width + 1):
                    if block.can_place(self.grid, x, y, self.grid_width, self.grid_height):
                        return True
        return False