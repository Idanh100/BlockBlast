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
        
        # Initialize highlighted cells to empty list each time a new action is taken
        self.highlighted_cells = []
        self.highlight_color = None
        self.valid_placement = False

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
                for i, block_key in enumerate(ui_elements["blocks"]):
                    if ui_elements["blocks"][block_key].collidepoint(event.pos):
                        self.dragging_block = observation['available_blocks'][i]
                        self.dragging_block_index = i
                        mouse_x, mouse_y = event.pos
                        self.offset_x = self.dragging_block.rect.x - mouse_x
                        self.offset_y = self.dragging_block.rect.y - mouse_y
                        break
            
            elif event.type == MOUSEBUTTONUP and self.dragging_block:
                # Calculate grid position
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
                self.dragging_block.rect.x = ui_elements["blocks"][f"block_{self.dragging_block_index}"].x
                self.dragging_block.rect.y = ui_elements["blocks"][f"block_{self.dragging_block_index}"].y
                self.dragging_block = None
                self.dragging_block_index = None
                self.highlighted_cells = []  # Clear highlighted cells when dropping
                self.highlight_color = None
                self.valid_placement = False
            
            elif event.type == MOUSEMOTION and self.dragging_block:
                # Update block position while dragging
                mouse_x, mouse_y = event.pos
                self.dragging_block.rect.x = mouse_x + self.offset_x
                self.dragging_block.rect.y = mouse_y + self.offset_y
                
                # Calculate potential grid position
                grid_x, grid_y = self._calculate_grid_position((mouse_x, mouse_y), ui_elements)
                
                # Check if placement is valid before highlighting
                self.valid_placement = self.dragging_block.can_place(
                    observation['grid'], 
                    grid_x, 
                    grid_y, 
                    len(observation['grid'][0]), 
                    len(observation['grid'])
                )
                
                # Only highlight cells if placement is valid
                if self.valid_placement:
                    self.highlighted_cells = self._get_highlighted_cells(mouse_x, mouse_y, ui_elements)
                    self.highlight_color = self.dragging_block.color
                else:
                    self.highlighted_cells = []
                    self.highlight_color = None
        
        return action

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
        if not self.dragging_block:
            return []
            
        # Get top-left grid position for the block using the same logic as _calculate_grid_position
        grid_x, grid_y = self._calculate_grid_position((mouse_x, mouse_y), ui_elements)
        
        # Create a list of cells covered by the block
        cells = []
        for y in range(self.dragging_block.height):
            for x in range(self.dragging_block.width):
                if self.dragging_block.shape[y][x] == 1:
                    cells.append((grid_x + x, grid_y + y))
        
        return cells