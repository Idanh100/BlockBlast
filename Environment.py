class Environment:
    def __init__(self):
        self.grid_origin_x = 40
        self.grid_origin_y = 150
        self.grid_size = 40
    
    def get_observation(self, state):
        """Returns the current state of the game as an observation."""
        return {
            'grid': state.grid,
            'available_blocks': state.available_blocks,
            'score': state.score,
            'lines_cleared': state.lines_cleared,
            'game_over': state.game_over
        }
    
    def step(self, state, action):
        """Apply the action to the game state and return reward and done status."""
        reward, done = 0, False
        
        if action['type'] == 'place_block':
            block_index = action['block_index']
            block = state.available_blocks[block_index]
            
            if block is not None:
                grid_x, grid_y = action['grid_x'], action['grid_y']
                
                if block.can_place(state.grid, grid_x, grid_y, state.grid_width, state.grid_height):
                    block.place(state.grid, grid_x, grid_y)
                    lines_cleared, score_gained = state.check_clear_lines()
                    reward = score_gained
                    state.mark_block_as_placed(block_index)
                    
                    if not state.can_place_any_block():
                        state.game_over = done = True
        
        elif action['type'] == 'restart':
            state.reset()
        
        return reward, done
    
    def grid_to_pixel(self, grid_x, grid_y):
        """Convert grid coordinates to pixel coordinates."""
        return (self.grid_origin_x + grid_x * self.grid_size, 
                self.grid_origin_y + grid_y * self.grid_size)
    
    def pixel_to_grid(self, pixel_x, pixel_y):
        """Convert pixel coordinates to grid coordinates."""
        return (round((pixel_x - self.grid_origin_x) / self.grid_size),
                round((pixel_y - self.grid_origin_y) / self.grid_size))