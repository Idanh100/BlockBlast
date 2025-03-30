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
        """
        Check if block can be placed at the specified grid position.
        
        Args:
            grid: The current game grid
            grid_x, grid_y: The top-left grid position to try placing the block
            grid_width, grid_height: The dimensions of the grid
            
        Returns:
            bool: True if the block can be placed, False otherwise
        """
        for y in range(self.height):
            for x in range(self.width):
                if self.shape[y][x] == 1:
                    # Check if position is valid (within grid bounds)
                    if grid_x + x < 0 or grid_x + x >= grid_width or grid_y + y < 0 or grid_y + y >= grid_height:
                        return False
                    # Check if cell is already occupied
                    if grid[grid_y + y][grid_x + x] is not None:
                        return False
        return True
    
    def place(self, grid, grid_x, grid_y):
        """
        Place the block on the grid at the specified position.
        
        Args:
            grid: The current game grid
            grid_x, grid_y: The top-left grid position to place the block
        """
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
        self.grid_width = 8
        self.grid_height = 8
        self.grid = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # Game state
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        
        # Create initial blocks with adjusted positioning
        self.available_blocks = self.generate_initial_blocks()
    
    def generate_initial_blocks(self):
        """Generate the initial set of blocks for a new game."""
        blocks = []
        
        # Set a position for the "Available Blocks" label (for reference)
        label_y = 50  # Assume this is the Y position of the label text
        block_y_start = label_y + 50  # Start below the label, adjusting for spacing
        
        # Red block (likely a square block from the description)
        red_shape = [[1, 1, 1], 
                     [1, 1, 1], 
                     [1, 1, 1]]
        red_block = Block(red_shape, self.RED, (60, block_y_start))  # Placed below the label
        blocks.append(red_block)
        
        # Yellow block (likely a horizontal line)
        yellow_shape = [[1, 1, 1, 1, 1]]
        yellow_block = Block(yellow_shape, self.YELLOW, (170, block_y_start))  # Placed below the label
        blocks.append(yellow_block)
        
        # Orange block (another horizontal line, could be different in size)
        orange_shape = [[1, 1, 1, 1, 1]]
        orange_block = Block(orange_shape, self.ORANGE, (280, block_y_start))  # Placed below the label
        blocks.append(orange_block)
        
        return blocks
    
    def generate_new_block(self, index):
        """
        Generate a new block to replace one that was placed.
        
        Args:
            index: Index of the block to be replaced
            
        Returns:
            Block: A new Block object
        """
        # More block variety for different slots
        if index == 0:  # Red block slot - larger blocks
            shapes = [
                [[1, 1, 1], [1, 1, 1], [1, 1, 1]],  # 3x3
                [[1, 1], [1, 1]],  # 2x2
                [[1, 1, 1], [1, 1, 1]],  # 3x2
                [[1, 1], [1, 1], [1, 1]]  # 2x3
            ]
            shape = random.choice(shapes)
            return Block(shape, self.RED, (60, 600))
        elif index == 1:  # Yellow block slot - horizontal lines
            shapes = [
                [[1, 1, 1, 1, 1]],  # 1x5
                [[1, 1, 1, 1]],  # 1x4
                [[1, 1, 1]],  # 1x3
                [[1, 1]]  # 1x2
            ]
            shape = random.choice(shapes)
            return Block(shape, self.YELLOW, (170, 600))
        else:  # Orange block slot - vertical lines and L-shapes
            shapes = [
                [[1], [1], [1], [1], [1]],  # 5x1
                [[1], [1], [1], [1]],  # 4x1
                [[1], [1], [1]],  # 3x1
                [[1, 1], [1, 0]]  # L-shape
            ]
            shape = random.choice(shapes)
            return Block(shape, self.ORANGE, (280, 600))
    
    def check_clear_lines(self):
        """
        Check and clear completed rows and columns.
        
        Returns:
            tuple: (lines_cleared, score_gained)
        """
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
        
        # Calculate score - add points based on number of lines cleared at once
        # This creates a bonus for clearing multiple lines simultaneously
        score_gain = 0
        if lines_cleared > 0:
            # Base score + exponential bonus for multiple lines
            score_gain = lines_cleared * 10 + (lines_cleared - 1) * 5
            self.score += score_gain
        
        # Update total lines cleared
        self.lines_cleared += lines_cleared
        
        return lines_cleared, score_gain
    
    def can_place_any_block(self):
        """
        Check if any available block can be placed anywhere on the grid.
        
        Returns:
            bool: True if at least one block can be placed, False otherwise
        """
        for block in self.available_blocks:
            for y in range(self.grid_height - block.height + 1):
                for x in range(self.grid_width - block.width + 1):
                    if block.can_place(self.grid, x, y, self.grid_width, self.grid_height):
                        return True
        return False
