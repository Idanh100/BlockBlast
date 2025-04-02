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
        
        # Track placed blocks for regeneration
        self.placed_blocks_count = 0
    
    def generate_initial_blocks(self):
        """Generate the initial set of blocks for a new game."""
        blocks = []
        
        # Position for blocks below "Available Blocks" text
        # These positions are for the original blocks - no grid offsets needed here
        # The blocks should appear at their actual screen positions
        blocks_y = 580  # Position below the "Available Blocks" text
        
        # Red block (likely a square block from the description)
        red_shape = [[1, 1, 1], 
                     [1, 1, 1], 
                     [1, 1, 1]]
        red_block = Block(red_shape, self.RED, (20, blocks_y))
        blocks.append(red_block)
        
        # Yellow block (likely a horizontal line)
        yellow_shape = [[1, 1, 1, 1, 1]]
        yellow_block = Block(yellow_shape, self.YELLOW, (160, blocks_y))
        blocks.append(yellow_block)
        
        # Orange block (another horizontal line, could be different in size)
        orange_shape = [[1, 1, 1, 1, 1]]
        orange_block = Block(orange_shape, self.ORANGE, (280, blocks_y))
        blocks.append(orange_block)
        
        return blocks
    
    def generate_new_blocks(self):
        """
        Generate a new set of blocks to replace all that were placed.
        
        Returns:
            List of new Block objects
        """
        # Position for new blocks - below "Available Blocks" text
        blocks_y = 580
        blocks = []
        
        # Generate red block
        red_shapes = [
            [[1, 1, 1], [1, 1, 1], [1, 1, 1]],  # 3x3
            [[1, 1], [1, 1]],  # 2x2
            [[1, 1, 1], [1, 1, 1]],  # 3x2
            [[1, 1], [1, 1], [1, 1]]  # 2x3
        ]
        red_shape = random.choice(red_shapes)
        red_block = Block(red_shape, self.RED, (20, blocks_y))
        blocks.append(red_block)
        
        # Generate yellow block
        yellow_shapes = [
            [[1, 1, 1, 1, 1]],  # 1x5
            [[1, 1, 1, 1]],  # 1x4
            [[1, 1, 1]],  # 1x3
            [[1, 1]]  # 1x2
        ]
        yellow_shape = random.choice(yellow_shapes)
        yellow_block = Block(yellow_shape, self.YELLOW, (160, blocks_y))
        blocks.append(yellow_block)
        
        # Generate orange block
        orange_shapes = [
            [[1], [1], [1], [1], [1]],  # 5x1
            [[1], [1], [1], [1]],  # 4x1
            [[1], [1], [1]],  # 3x1
            [[1, 1], [1, 0]]  # L-shape
        ]
        orange_shape = random.choice(orange_shapes)
        orange_block = Block(orange_shape, self.ORANGE, (280, blocks_y))
        blocks.append(orange_block)
        
        return blocks
    
    def mark_block_as_placed(self, block_index):
        """
        Mark a block as placed and handle block regeneration logic.
        
        Args:
            block_index: Index of the block that was placed
            
        Returns:
            bool: True if all blocks were placed and new ones were generated
        """
        # Set the block to None to indicate it's been placed
        self.available_blocks[block_index] = None
        self.placed_blocks_count += 1
        
        # Check if all blocks have been placed
        if self.placed_blocks_count >= 3:
            # Generate new blocks
            self.available_blocks = self.generate_new_blocks()
            self.placed_blocks_count = 0
            return True
        
        return False
    
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
            # Skip blocks that have been placed (set to None)
            if block is None:
                continue
                
            for y in range(self.grid_height - block.height + 1):
                for x in range(self.grid_width - block.width + 1):
                    if block.can_place(self.grid, x, y, self.grid_width, self.grid_height):
                        return True
        return False