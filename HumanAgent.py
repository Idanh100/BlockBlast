import pygame
from pygame.locals import *

class HumanAgent:
    def __init__(self):
        self.dragging_block = None
        self.dragging_block_index = None
        self.offset_x = 0
        self.offset_y = 0
    
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
                
                # Create place block action
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
            
            elif event.type == MOUSEMOTION and self.dragging_block:
                # Update block position while dragging
                mouse_x, mouse_y = event.pos
                self.dragging_block.rect.x = mouse_x + self.offset_x
                self.dragging_block.rect.y = mouse_y + self.offset_y
        
        return action
    
    def _calculate_grid_position(self, mouse_pos, ui_elements):
        """
        Calculate the grid position from mouse position, adjusted for block size.
        
        Args:
            mouse_pos: The current mouse position
            ui_elements: Dictionary of UI elements
            
        Returns:
            tuple: (grid_x, grid_y) coordinates for block placement
        """
        mouse_x, mouse_y = mouse_pos
        grid_origin_x, grid_origin_y = ui_elements["grid_origin"]
        grid_size = ui_elements["grid_size"]
        
        # Calculate top-left corner of block placement
        if self.dragging_block:
            # Adjust by half the width and height of the block to center placement
            width_offset = (self.dragging_block.width * grid_size) / 2
            height_offset = (self.dragging_block.height * grid_size) / 2
            
            grid_x = int((mouse_x - grid_origin_x - width_offset) / grid_size) + self.dragging_block.width // 2
            grid_y = int((mouse_y - grid_origin_y - height_offset) / grid_size) + self.dragging_block.height // 2
            
            # Adjust for block size to ensure correct top-left placement
            grid_x -= self.dragging_block.width // 2
            grid_y -= self.dragging_block.height // 2
        else:
            grid_x = int((mouse_x - grid_origin_x) / grid_size)
            grid_y = int((mouse_y - grid_origin_y) / grid_size)
        
        return grid_x, grid_y