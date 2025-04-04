import pygame
from pygame.locals import *

class HumanAgent:
    def __init__(self):
        self.dragging_block = None
        self.dragging_block_index = None
        self.offset_x = self.offset_y = 0
        self.highlighted_cells = []
        self.highlight_color = None
        self.valid_placement = False
        self.last_valid_position = None
        self.snap_threshold = 15
        self.complete_rows = []
        self.complete_cols = []

    def get_menu_action(self, ui_elements):
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
        for event in pygame.event.get():
            if event.type == QUIT:
                return "quit"
            
            if event.type == MOUSEBUTTONDOWN:
                if ui_elements["menu_button"].collidepoint(event.pos):
                    return "menu"
        return None
    
    def get_action(self, observation, ui_elements):
        action = {'type': 'none'}
        
        # Reset highlighted cells if not dragging
        if not self.dragging_block:
            self.highlighted_cells = []
            self.highlight_color = None
            self.valid_placement = False
            self.last_valid_position = None
            self.complete_rows = []
            self.complete_cols = []

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            
            if event.type == MOUSEBUTTONDOWN:
                # Check for block clicking with improved hitbox detection
                for block_key in ui_elements["blocks"]:
                    block_index = int(block_key.split('_')[1])
                    if block_index < len(observation['available_blocks']) and observation['available_blocks'][block_index] is not None:
                        block = observation['available_blocks'][block_index]
                        
                        # Create proper hitbox for the block based on its actual shape
                        mouse_x, mouse_y = event.pos
                        grid_size = ui_elements["grid_size"]
                        
                        # Check if mouse is over any cell of the block
                        is_over_block = False
                        for y in range(block.height):
                            for x in range(block.width):
                                if block.shape[y][x] == 1:
                                    cell_rect = pygame.Rect(
                                        block.rect.x + x * grid_size,
                                        block.rect.y + y * grid_size,
                                        grid_size,
                                        grid_size
                                    )
                                    if cell_rect.collidepoint(mouse_x, mouse_y):
                                        is_over_block = True
                                        break
                            if is_over_block:
                                break
                                
                        if is_over_block:
                            self.dragging_block = block
                            self.dragging_block_index = block_index
                            self.offset_x = block.rect.x - mouse_x
                            self.offset_y = block.rect.y - mouse_y
                            break
            
            elif event.type == MOUSEBUTTONUP and self.dragging_block:
                # Get grid position for placement
                grid_x, grid_y = self.last_valid_position if (self.last_valid_position and self.valid_placement) else self._calculate_grid_position(event.pos, ui_elements)
                
                # Create place block action only if placement is valid
                if self.valid_placement:
                    action = {
                        'type': 'place_block',
                        'block_index': self.dragging_block_index,
                        'grid_x': grid_x,
                        'grid_y': grid_y
                    }
                
                # Reset block position and dragging state
                block_key = f"block_{self.dragging_block_index}"
                if self.dragging_block_index < len(ui_elements["blocks"]) and block_key in ui_elements["blocks"]:
                    original_rect = ui_elements["blocks"][block_key]
                    self.dragging_block.rect.x = original_rect.x
                    self.dragging_block.rect.y = original_rect.y
                
                # Reset all dragging states
                self.dragging_block = None
                self.dragging_block_index = None
                self.highlighted_cells = []
                self.highlight_color = None
                self.valid_placement = False
                self.last_valid_position = None
                self.complete_rows = []
                self.complete_cols = []
            
            elif event.type == MOUSEMOTION and self.dragging_block:
                # Update block position while dragging
                mouse_x, mouse_y = event.pos
                self.dragging_block.rect.x = mouse_x + self.offset_x
                self.dragging_block.rect.y = mouse_y + self.offset_y
                
                # Try to find a valid placement near the cursor
                self._find_valid_placement_near(mouse_x, mouse_y, ui_elements, observation)
        
        return action

    def _find_valid_placement_near(self, mouse_x, mouse_y, ui_elements, observation):
        grid_size = ui_elements["grid_size"]
        grid_origin_x, grid_origin_y = ui_elements["grid_origin"]
        
        # Try exact position under cursor first
        exact_grid_x, exact_grid_y = self._calculate_grid_position((mouse_x, mouse_y), ui_elements)
        
        # Check if current position is valid
        if self._check_valid_placement(exact_grid_x, exact_grid_y, observation):
            self.valid_placement = True
            self.last_valid_position = (exact_grid_x, exact_grid_y)
            self.highlighted_cells = self._get_highlighted_cells_for_position(exact_grid_x, exact_grid_y)
            self.highlight_color = self.dragging_block.color
            self._check_potential_line_completions(exact_grid_x, exact_grid_y, observation)
            return
            
        # Search in a small area around the cursor for valid positions
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
                    
                    # Adjust snap threshold based on grid size
                    adjusted_threshold = self.snap_threshold * (grid_size / 40.0)
                    
                    if distance <= adjusted_threshold:
                        self.valid_placement = True
                        self.last_valid_position = (test_grid_x, test_grid_y)
                        self.highlighted_cells = self._get_highlighted_cells_for_position(test_grid_x, test_grid_y)
                        self.highlight_color = self.dragging_block.color
                        self._check_potential_line_completions(test_grid_x, test_grid_y, observation)
                        return
        
        # If we get here, no valid position was found nearby
        self.valid_placement = False
        self.highlighted_cells = []
        self.highlight_color = None
        self.last_valid_position = None
        self.complete_rows = []
        self.complete_cols = []

    def _check_potential_line_completions(self, grid_x, grid_y, observation):
        if not self.dragging_block:
            return
        
        grid = observation['grid']
        grid_width = len(grid[0])
        grid_height = len(grid)
        
        # Create a temporary grid with the block placed
        temp_grid = [row[:] for row in grid]  # Deep copy
        
        # Place the block in the temporary grid
        for y in range(self.dragging_block.height):
            for x in range(self.dragging_block.width):
                if self.dragging_block.shape[y][x] == 1:
                    if 0 <= grid_y + y < grid_height and 0 <= grid_x + x < grid_width:
                        temp_grid[grid_y + y][grid_x + x] = self.dragging_block.color
        
        # Check rows that would be completed
        self.complete_rows = [y for y in range(grid_height) 
                           if all(temp_grid[y][x] is not None for x in range(grid_width))]
        
        # Check columns that would be completed
        self.complete_cols = [x for x in range(grid_width) 
                           if all(temp_grid[y][x] is not None for y in range(grid_height))]

    def _check_valid_placement(self, grid_x, grid_y, observation):
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
        mouse_x, mouse_y = mouse_pos
        grid_origin_x, grid_origin_y = ui_elements["grid_origin"]
        grid_size = ui_elements["grid_size"]
        
        if self.dragging_block:
            # Calculate the top-left corner of where the block would be
            block_top_left_x = mouse_x + self.offset_x
            block_top_left_y = mouse_y + self.offset_y
            
            # Convert to grid coordinates
            grid_x = int((block_top_left_x - grid_origin_x) / grid_size)
            grid_y = int((block_top_left_y - grid_origin_y) / grid_size)
            
            return grid_x, grid_y
        else:
            # If not dragging, just convert mouse position to grid coordinates
            return (int((mouse_x - grid_origin_x) / grid_size), 
                    int((mouse_y - grid_origin_y) / grid_size))

    def _get_highlighted_cells_for_position(self, grid_x, grid_y):
        if not self.dragging_block:
            return []
            
        return [(grid_x + x, grid_y + y) 
                for y in range(self.dragging_block.height) 
                for x in range(self.dragging_block.width) 
                if self.dragging_block.shape[y][x] == 1]