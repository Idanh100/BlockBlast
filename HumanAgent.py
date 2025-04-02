import pygame
from pygame.locals import *

class HumanAgent:
    def __init__(self):
        self.dragging_block = None
        self.dragging_block_index = None
        self.offset_x = 0
        self.offset_y = 0
        self.highlighted_cells = []  # To store the highlighted cells
        self.highlight_color = None  # To store the color for highlighting
        self.valid_placement = False  # Flag to track if current placement is valid
        self.last_valid_position = None  # Store the last valid grid position
        self.snap_threshold = 15  # Distance in pixels to snap to grid

    def get_menu_action(self, ui_elements):
        """
        Get action from the menu screen.
        
        Args:
            ui_elements (dict): Dictionary of UI elements with their rects
        
        Returns:
            str: The action to take ('start', 'quit', None)
        """
        for event in pygame.event.get():
            if event.type == QUIT:
                return "quit"
            
            if event.type == MOUSEBUTTONDOWN:
                if ui_elements["start_button"].collidepoint(event.pos):
                    return "start"
                if ui_elements["quit_button"].collidepoint(event.pos):
                    return "quit"
        
        return None
    
    def get_game_over_action(self, ui_elements):
        """
        Get action from the game over screen.
        
        Args:
            ui_elements (dict): Dictionary of UI elements with their rects
        
        Returns:
            str: The action to take ('menu', 'quit', None)
        """
        for event in pygame.event.get():
            if event.type == QUIT:
                return "quit"
            
            if event.type == MOUSEBUTTONDOWN:
                if ui_elements["menu_button"].collidepoint(event.pos):
                    return "menu"
        
        return None
    
    def get_action(self, observation, ui_elements):
        """
        Get action from the user.
        
        Args:
            observation (dict): The current game state
            ui_elements (dict): Dictionary of UI elements with their rects
        
        Returns:
            dict: The action to take
        """
        action = {
            'type': 'none'
        }
        
        # Keep highlighted cells from last frame if we're still dragging
        if not self.dragging_block:
            self.highlighted_cells = []
            self.highlight_color = None
            self.valid_placement = False
            self.last_valid_position = None

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            
            if event.type == MOUSEBUTTONDOWN:
                # Check if settings button is clicked
                if ui_elements["settings_button"].collidepoint(event.pos):
                    # Settings action would go here
                    pass
                
                # Check if a block is clicked
                for block_key in ui_elements["blocks"]:
                    if ui_elements["blocks"][block_key].collidepoint(event.pos):
                        # Extract the block index from the key (block_0, block_1, etc.)
                        block_index = int(block_key.split('_')[1])
                        
                        # Make sure this block exists in available_blocks
                        if block_index < len(observation['available_blocks']) and observation['available_blocks'][block_index] is not None:
                            self.dragging_block = observation['available_blocks'][block_index]
                            self.dragging_block_index = block_index
                            mouse_x, mouse_y = event.pos
                            self.offset_x = self.dragging_block.rect.x - mouse_x
                            self.offset_y = self.dragging_block.rect.y - mouse_y
                            break
            
            elif event.type == MOUSEBUTTONUP and self.dragging_block:
                # Use last valid position if available, otherwise calculate from current mouse pos
                if self.last_valid_position and self.valid_placement:
                    grid_x, grid_y = self.last_valid_position
                else:
                    grid_x, grid_y = self._calculate_grid_position(event.pos, ui_elements)
                
                # Create place block action only if placement is valid
                if self.valid_placement:
                    action = {
                        'type': 'place_block',
                        'block_index': self.dragging_block_index,
                        'grid_x': grid_x,
                        'grid_y': grid_y
                    }
                
                # Reset dragging state
                if self.dragging_block_index < len(ui_elements["blocks"]) and f"block_{self.dragging_block_index}" in ui_elements["blocks"]:
                    self.dragging_block.rect.x = ui_elements["blocks"][f"block_{self.dragging_block_index}"].x
                    self.dragging_block.rect.y = ui_elements["blocks"][f"block_{self.dragging_block_index}"].y
                self.dragging_block = None
                self.dragging_block_index = None
                self.highlighted_cells = []  # Clear highlighted cells when dropping
                self.highlight_color = None
                self.valid_placement = False
                self.last_valid_position = None
            
            elif event.type == MOUSEMOTION and self.dragging_block:
                # Update block position while dragging
                mouse_x, mouse_y = event.pos
                self.dragging_block.rect.x = mouse_x + self.offset_x
                self.dragging_block.rect.y = mouse_y + self.offset_y
                
                # Try to find a valid placement near the cursor
                self._find_valid_placement_near(mouse_x, mouse_y, ui_elements, observation)
        
        return action

    def _find_valid_placement_near(self, mouse_x, mouse_y, ui_elements, observation):
        """
        Find a valid placement position near the cursor.
        If found, update highlighting and valid_placement flag.
        
        Args:
            mouse_x, mouse_y: Current mouse position
            ui_elements: Dictionary of UI elements
            observation: Current game state
        """
        grid_size = ui_elements["grid_size"]
        grid_origin_x, grid_origin_y = ui_elements["grid_origin"]
        grid_width = len(observation['grid'][0])
        grid_height = len(observation['grid'])
        
        # First try exact position under cursor
        exact_grid_x, exact_grid_y = self._calculate_grid_position((mouse_x, mouse_y), ui_elements)
        
        # Check if current position is valid
        if self._check_valid_placement(exact_grid_x, exact_grid_y, observation):
            self.valid_placement = True
            self.last_valid_position = (exact_grid_x, exact_grid_y)
            self.highlighted_cells = self._get_highlighted_cells_for_position(exact_grid_x, exact_grid_y)
            self.highlight_color = self.dragging_block.color
            return
            
        # If not valid, search in a small area around the cursor for valid positions
        # We'll search in a 3x3 cell area around the current grid position
        for y_offset in range(-1, 2):
            for x_offset in range(-1, 2):
                test_grid_x = exact_grid_x + x_offset
                test_grid_y = exact_grid_y + y_offset
                
                # Skip if we're at the exact position (already checked)
                if x_offset == 0 and y_offset == 0:
                    continue
                    
                # Check if this position is valid
                if self._check_valid_placement(test_grid_x, test_grid_y, observation):
                    # Calculate pixel distance to see if we're close enough to snap
                    test_pixel_x = grid_origin_x + test_grid_x * grid_size
                    test_pixel_y = grid_origin_y + test_grid_y * grid_size
                    
                    dx = (mouse_x + self.offset_x) - test_pixel_x
                    dy = (mouse_y + self.offset_y) - test_pixel_y
                    distance = (dx**2 + dy**2)**0.5
                    
                    if distance <= self.snap_threshold * grid_size / 40:  # Scaled by grid size
                        self.valid_placement = True
                        self.last_valid_position = (test_grid_x, test_grid_y)
                        self.highlighted_cells = self._get_highlighted_cells_for_position(test_grid_x, test_grid_y)
                        self.highlight_color = self.dragging_block.color
                        return
        
        # If we get here, no valid position was found nearby
        self.valid_placement = False
        self.highlighted_cells = []
        self.highlight_color = None
        self.last_valid_position = None

    def _check_valid_placement(self, grid_x, grid_y, observation):
        """
        Check if the current block can be placed at the given grid position.
        
        Args:
            grid_x, grid_y: Grid position to check
            observation: Current game state
            
        Returns:
            bool: True if placement is valid, False otherwise
        """
        if not self.dragging_block:
            return False
            
        return self.dragging_block.can_place(
            observation['grid'], 
            grid_x, 
            grid_y, 
            len(observation['grid'][0]), 
            len(observation['grid'])
        )
    
    def _calculate_grid_position(self, mouse_pos, ui_elements):
        """
        Calculate the grid position from mouse position, taking into account
        where the user grabbed the block.
        
        Args:
            mouse_pos: The current mouse position
            ui_elements: Dictionary of UI elements
            
        Returns:
            tuple: (grid_x, grid_y) coordinates for block placement
        """
        mouse_x, mouse_y = mouse_pos
        grid_origin_x, grid_origin_y = ui_elements["grid_origin"]
        grid_size = ui_elements["grid_size"]
        
        if self.dragging_block:
            # Calculate position based on the drag offset (where user grabbed the block)
            # This creates a more natural placement where blocks appear under the cursor
            
            # Calculate the top-left corner of where the block would be
            block_top_left_x = mouse_x + self.offset_x
            block_top_left_y = mouse_y + self.offset_y
            
            # Convert to grid coordinates
            grid_x = int((block_top_left_x - grid_origin_x) / grid_size)
            grid_y = int((block_top_left_y - grid_origin_y) / grid_size)
            
            return grid_x, grid_y
        else:
            # If not dragging, just convert mouse position to grid coordinates
            grid_x = int((mouse_x - grid_origin_x) / grid_size)
            grid_y = int((mouse_y - grid_origin_y) / grid_size)
            
            return grid_x, grid_y

    def _get_highlighted_cells_for_position(self, grid_x, grid_y):
        """
        Get the cells that would be highlighted for a specific grid position.
        
        Args:
            grid_x, grid_y: The grid position
            
        Returns:
            list: List of (x, y) tuples for cells to highlight
        """
        if not self.dragging_block:
            return []
            
        cells = []
        for y in range(self.dragging_block.height):
            for x in range(self.dragging_block.width):
                if self.dragging_block.shape[y][x] == 1:
                    cells.append((grid_x + x, grid_y + y))
        
        return cells
        
    def _get_highlighted_cells(self, mouse_x, mouse_y, ui_elements):
        """
        Calculate all grid cells that should be highlighted when dragging the block.
        
        Args:
            mouse_x: The x-coordinate of the mouse
            mouse_y: The y-coordinate of the mouse
            ui_elements: Dictionary of UI elements
            
        Returns:
            list: A list of tuples representing the highlighted grid positions
        """
        if not self.dragging_block or not self.last_valid_position:
            return []
            
        grid_x, grid_y = self.last_valid_position
        return self._get_highlighted_cells_for_position(grid_x, grid_y)