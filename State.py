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
                              self.width * 40, self.height * 40)
    
    def can_place(self, grid, grid_x, grid_y, grid_width, grid_height):
        """Check if block can be placed at the specified grid position."""
        for y in range(self.height):
            for x in range(self.width):
                if self.shape[y][x] == 1:
                    if (grid_x + x < 0 or grid_x + x >= grid_width or 
                        grid_y + y < 0 or grid_y + y >= grid_height or
                        grid[grid_y + y][grid_x + x] is not None):
                        return False
        return True
    
    def place(self, grid, grid_x, grid_y):
        """Place the block on the grid at the specified position."""
        for y in range(self.height):
            for x in range(self.width):
                if self.shape[y][x] == 1:
                    grid[grid_y + y][grid_x + x] = self.color


class State:
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset the game state to starting conditions."""
        # Define colors
        self.RED = (220, 70, 70)
        self.YELLOW = (240, 200, 50)
        self.ORANGE = (240, 130, 50)
        self.GREEN = (100, 200, 100)
        self.BLUE = (100, 100, 240)
        
        # Grid dimensions
        self.grid_width, self.grid_height = 8, 8
        self.grid = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # Game state
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        self.placed_blocks_count = 0
        
        # Create initial blocks
        self.available_blocks = self.generate_initial_blocks()
    
    def generate_initial_blocks(self):
        """Generate the initial set of blocks for a new game."""
        blocks_y = 580
        
        blocks = [
            Block([[1, 1, 1], [1, 1, 1], [1, 1, 1]], self.RED, (20, blocks_y)),
            Block([[1, 1, 1, 1, 1]], self.YELLOW, (160, blocks_y)),
            Block([[1, 1, 1, 1, 1]], self.ORANGE, (280, blocks_y))
        ]
        
        return blocks
    
    def generate_new_blocks(self):
        """Generate a new set of blocks to replace all that were placed."""
        blocks_y = 580
        
        # Block shape options
        red_shapes = [
            [[1, 1, 1], [1, 1, 1], [1, 1, 1]], [[1, 1], [1, 1]],
            [[1, 1, 1], [1, 1, 1]], [[1, 1], [1, 1], [1, 1]]
        ]
        yellow_shapes = [
            [[1, 1, 1, 1, 1]], [[1, 1, 1, 1]], [[1, 1, 1]], [[1, 1]]
        ]
        orange_shapes = [
            [[1], [1], [1], [1], [1]], [[1], [1], [1], [1]],
            [[1], [1], [1]], [[1, 1], [1, 0]]
        ]
        
        blocks = [
            Block(random.choice(red_shapes), self.RED, (20, blocks_y)),
            Block(random.choice(yellow_shapes), self.YELLOW, (160, blocks_y)),
            Block(random.choice(orange_shapes), self.ORANGE, (280, blocks_y))
        ]
        
        return blocks
    
    def mark_block_as_placed(self, block_index):
        """Mark a block as placed and handle block regeneration logic."""
        self.available_blocks[block_index] = None
        self.placed_blocks_count += 1
        
        if self.placed_blocks_count >= 3:
            self.available_blocks = self.generate_new_blocks()
            self.placed_blocks_count = 0
            return True
        
        return False
    
    def check_clear_lines(self):
        """Check and clear completed rows and columns."""
        lines_cleared = 0
        rows_to_clear = []
        cols_to_clear = []
        
        # Check rows
        for y in range(self.grid_height):
            if all(self.grid[y][x] is not None for x in range(self.grid_width)):
                rows_to_clear.append(y)
                lines_cleared += 1
        
        # Check columns
        for x in range(self.grid_width):
            if all(self.grid[y][x] is not None for y in range(self.grid_height)):
                cols_to_clear.append(x)
                lines_cleared += 1
        
        # Clear rows and columns
        for y in rows_to_clear:
            for x in range(self.grid_width):
                self.grid[y][x] = None
        
        for x in cols_to_clear:
            for y in range(self.grid_height):
                self.grid[y][x] = None
        
        # Calculate score
        score_gain = 0
        if lines_cleared > 0:
            score_gain = lines_cleared * 10 + (lines_cleared - 1) * 5
            self.score += score_gain
            self.lines_cleared += lines_cleared
        
        return lines_cleared, score_gain
    
    def can_place_any_block(self):
        """Check if any available block can be placed anywhere on the grid."""
        for block in self.available_blocks:
            if block is None:
                continue
                
            for y in range(self.grid_height - block.height + 1):
                for x in range(self.grid_width - block.width + 1):
                    if block.can_place(self.grid, x, y, self.grid_width, self.grid_height):
                        return True
        return False