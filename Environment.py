class Environment:
    def __init__(self):
        self.grid_origin_x = 40
        self.grid_origin_y = 150
        self.grid_size = 40
    
    def get_observation(self, state):
        """
        Returns the current state of the game as an observation.
        
        Args:
            state: The current State object
            
        Returns:
            dict: A dictionary containing the current game state
        """
        return {
            'grid': state.grid,
            'available_blocks': state.available_blocks,
            'score': state.score,
            'lines_cleared': state.lines_cleared,
            'game_over': state.game_over
        }
    
    def step(self, state, action):
        """
        Apply the action to the game state and return the reward and whether the game is done.
        
        Args:
            state (State): The current game state
            action (dict): The action to apply
                - type: The type of action ('place_block', 'restart', 'none')
                - block_index: The index of the block to place (if type is 'place_block')
                - grid_x: The grid x-coordinate to place the block (if type is 'place_block')
                - grid_y: The grid y-coordinate to place the block (if type is 'place_block')
        
        Returns:
            tuple: (reward, done)
                - reward: The reward for this action
                - done: Whether the game is done
        """
        reward = 0
        done = False
        
        if action['type'] == 'place_block':
            # Get the block to place
            block_index = action['block_index']
            block = state.available_blocks[block_index]
            
            # Calculate grid position
            grid_x = action['grid_x']
            grid_y = action['grid_y']
            
            # Try to place the block
            if block.can_place(state.grid, grid_x, grid_y, state.grid_width, state.grid_height):
                # Place the block
                block.place(state.grid, grid_x, grid_y)
                
                # Check for line clears and get score
                lines_cleared, score_gained = state.check_clear_lines()
                
                # Set reward
                reward = score_gained
                
                # Generate new block
                state.available_blocks[block_index] = state.generate_new_block(block_index)
                
                # Check if game is over
                if not state.can_place_any_block():
                    state.game_over = True
                    done = True
        
        elif action['type'] == 'restart':
            state.reset()
        
        return reward, done
    
    def grid_to_pixel(self, grid_x, grid_y):
        """
        Convert grid coordinates to pixel coordinates.
        
        Args:
            grid_x, grid_y: The grid coordinates
            
        Returns:
            tuple: (pixel_x, pixel_y) pixel coordinates
        """
        pixel_x = self.grid_origin_x + grid_x * self.grid_size
        pixel_y = self.grid_origin_y + grid_y * self.grid_size
        return pixel_x, pixel_y
    
    def pixel_to_grid(self, pixel_x, pixel_y):
        """
        Convert pixel coordinates to grid coordinates.
        
        Args:
            pixel_x, pixel_y: The pixel coordinates
            
        Returns:
            tuple: (grid_x, grid_y) grid coordinates
        """
        grid_x = round((pixel_x - self.grid_origin_x) / self.grid_size)
        grid_y = round((pixel_y - self.grid_origin_y) / self.grid_size)
        return grid_x, grid_y