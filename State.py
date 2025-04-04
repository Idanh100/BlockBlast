import pygame
import random

class Block:
    def __init__(self, shape, color, position):
        self.shape = shape
        self.color = color
        self.width = len(shape[0])
        self.height = len(shape)
        self.dragging = False
        # The rect will be updated with proper scaling when drawn
        self.rect = pygame.Rect(position[0], position[1], 
                              self.width * 60, self.height * 60)  # Initial size uses larger cells
    
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
        self.PURPLE = (180, 100, 240)  # Added purple color
        
        # All available colors
        self.colors = [self.RED, self.YELLOW, self.ORANGE, self.GREEN, self.BLUE, self.PURPLE]
        
        # Grid dimensions
        self.grid_width, self.grid_height = 8, 8
        self.grid = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # Game state
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        self.placed_blocks_count = 0
        
        # Create initial blocks
        self.available_blocks = self.generate_new_blocks()
    
    def generate_all_shapes(self):
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
            "dot": [[1]],
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
    
    def get_random_shape(self):
        """Get a random shape from all available shapes."""
        all_shapes = self.generate_all_shapes()
        shape_name = random.choice(list(all_shapes.keys()))
        return all_shapes[shape_name]
    
    def generate_initial_blocks(self):
        """Generate the initial set of blocks for a new game."""
        # Default y position - actual position will be set in Graphics
        blocks_y = 580
        
        # Generate random blocks
        blocks = []
        for i in range(3):
            blocks.append(
                Block(
                    self.get_random_shape(),
                    random.choice(self.colors),
                    (20 + i * 140, blocks_y)
                )
            )
        
        return blocks
    
    def generate_new_blocks(self):
        """Generate a new set of blocks to replace all that were placed."""
        # Default y position - actual position will be set in Graphics
        blocks_y = 580
        
        # Generate three completely random blocks with random colors
        blocks = []
        for _ in range(3):
            blocks.append(
                Block(
                    self.get_random_shape(),
                    random.choice(self.colors),
                    (20, blocks_y)
                )
            )
        
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