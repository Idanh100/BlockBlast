State.py
import pygame
import random

class Block:
    def __init__(self, shape, color, position):
        self.shape = shape
        self.color = color
        self.width = len(shape[0])  # Width of the block
        self.height = len(shape)  # Height of the block
        self.rect = pygame.Rect(position[0], position[1], 
                               self.width * 40, 
                               self.height * 40)  # Using 40 as GRID_SIZE
    
    def can_place(self, grid, grid_x, grid_y, grid_width, grid_height):
        """
        Checks if the block can be placed on the grid at the specified location.
        """
        for y in range(self.height):
            for x in range(self.width):
                if self.shape[y][x] == 1:
                    # Check if the block is within grid bounds
                    if not (0 <= grid_x + x < grid_width and 0 <= grid_y + y < grid_height):
                        return False
                    # Check if the target cell is already occupied
                    if grid[grid_y + y][grid_x + x] is not None:
                        return False
        return True
    
    def place(self, grid, grid_x, grid_y):
        """
        Places the block on the grid by marking occupied cells with the block color.
        """
        for y in range(self.height):
            for x in range(self.width):
                if self.shape[y][x] == 1:
                    grid[grid_y + y][grid_x + x] = self.color


class State:
    def __init__(self):
        self.reset()
    
    def reset(self):
        """
        Initializes or resets the game state.
        """
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
        """
        Generates a list of 3 available blocks to place, each with a random shape and random color.
        The blocks will be placed in empty slots to avoid overlapping.
        """
        blocks = []

        # List of available colors
        colors = [self.RED, self.YELLOW, self.ORANGE]

        # Shapes for different block sizes
        shapes = [
            [[1, 1, 1],  # 3x3 block
            [1, 1, 1], 
            [1, 1, 1]],

            [[1, 1, 1, 1, 1]],  # 1x5 block

            [[1, 1, 1, 1]],  # 1x4 block

            [[1, 1, 1]],  # 1x3 block

            # Additional Shapes
            [[1, 0, 0], [1, 1, 1]],  # L-Shape (3x2)
            [[0, 1, 0], [1, 1, 1]],  # T-Shape (3x2)
            [[1, 1, 0], [0, 1, 1]],  # Z-Shape (2x3)
            [[0, 1, 1], [1, 1, 0]],  # S-Shape (2x3)
            [[1, 1], [1, 1]],  # Square (2x2)
            [[0, 1, 0], [1, 1, 1], [0, 1, 0]],  # Plus Sign (3x3)
            [[1], [1], [1], [1], [1]]  # Tall "I" Block (1x5)
        ]

        # List of already used X positions (in terms of grid placement)
        used_positions = []  # This will store the starting X positions where blocks are placed

        # Generate 3 initial blocks
        for i in range(3):
            # Select a random shape and a random color
            shape = random.choice(shapes)
            color = random.choice(colors)

            # Determine the width of the block (width of the shape multiplied by grid size)
            block_width = len(shape[0]) * 40  # 40 is the GRID_SIZE (adjust as needed)

            # Find an empty spot to place the new block
            # We'll ensure the new block doesn't overlap by checking the used X positions
            x_position = 60  # Starting X position for the first block

            # Check for the next available empty position
            while x_position in used_positions:
                x_position += (block_width + 20)  # Move over to the next empty slot

            # Add the new position to the list of used positions
            used_positions.append(x_position)

            # Set the Y position (all blocks spawn at the same Y position for simplicity)
            y_position = 600

            # Create the block and add it to the list
            block = Block(shape, color, (x_position, y_position))
            blocks.append(block)

        return blocks
    
    def generate_new_block(self, index):
        """
        Generates a new block when an old one is used up or cleared, with a random color for each shape.
        """
        # List of available colors
        colors = [self.RED, self.YELLOW, self.ORANGE]
    
        # Shapes for different block sizes
        shapes = [
            # 3x3 block
            [[1, 1, 1], 
             [1, 1, 1], 
             [1, 1, 1]],
        
            # 2x2 block
            [[1, 1], 
             [1, 1]], 
        
            # 3x2 block
            [[1, 1, 1], 
             [1, 1, 1]],
        
            # 1x5 block
            [[1, 1, 1, 1, 1]], 
        
            # 1x4 block
            [[1, 1, 1, 1]], 
        
            # 1x3 block
            [[1, 1, 1]],
        
            # Additional Shapes
            [[1, 0, 0], [1, 1, 1]],  # L-Shape (3x2)
            [[0, 1, 0], [1, 1, 1]],  # T-Shape (3x2)
            [[1, 1, 0], [0, 1, 1]],  # Z-Shape (2x3)
            [[0, 1, 1], [1, 1, 0]],  # S-Shape (2x3)
            [[1, 1], [1, 1]],  # Square (2x2)
            [[0, 1, 0], [1, 1, 1], [0, 1, 0]],  # Plus Sign (3x3)
            [[1], [1], [1], [1], [1]]  # Tall "I" Block (1x5)
        ]
    
        # Select a random shape
        shape = random.choice(shapes)
    
        # Select a random color from the available colors
        color = random.choice(colors)
    
        # Determine the starting position based on the block size (you can adjust this)
        starting_position = (60, 600)  # You may need to adjust this based on the layout
    
        # Return a new block with a random shape and color
        return Block(shape, color, starting_position)
    
    def check_clear_lines(self):
        """
        Clears rows or columns that are completely filled with blocks.
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
        
        # Update total lines cleared
        self.lines_cleared += lines_cleared
        