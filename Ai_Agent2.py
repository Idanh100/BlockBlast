import pygame
import torch
import copy
import random
from State2 import State
from Environment2 import Environment
from Model import DQN
from Block import Block

class Ai_Agent:
    def __init__(self, model=None):
        """Initialize AI Agent.
        
        Args:
            model: DQN model instance for choosing actions. If None, creates a new one.
        """
        pygame.init()
        info = pygame.display.get_desktop_sizes()[0]
        self.width, self.height = info

        self.GRID_ORIGIN_Y = self.height / 10
        self.GRID_SIZE = self.width / 30
        self.GRID_ORIGIN_X = (self.width / 2) - (self.GRID_SIZE * 4)
        self.GRID_MARGIN = 4

        self.model = model if model else DQN()  # יוצר DQN אם לא סופקה
        self.selected_block = None  # התאמה לממשק של Main2.py
        self.env = Environment(State())
        

    def get_action(self, state):
        """Get the best action using the DQN model.
        
        Returns:
            tuple: (block, position_in_pixels) if action found, None otherwise
        """
        moves = self.get_all_moves(state)
                
        # בחר מהלך עם ה-Q-value הגבוה ביותר או אקראי עם הסתברות epsilon
        if random.random() < self.get_epsilon() or len(moves) == 1:
            # בחירה אקראית
            best_move = random.choice(moves)
            return self.move_to_action(best_move)

        after_state_tensors = self.get_after_states(moves, state)

        with torch.no_grad():  # אל תחשב gradients בהערכה
            q_values = self.model(after_state_tensors)

        best_idx = torch.argmax(q_values)
        best_move = moves[best_idx]
        return self.move_to_action(best_move)
      
        
    
    def get_all_moves (self, state):
        # קבל את כל המהלכים האפשריים רק עבור הבלוקים הזמינים
        moves = []                          # move to function
        for block in state.Blocks:
            shape_h = len(block.shape)
            shape_w = len(block.shape[0]) if shape_h > 0 else 0
            
            # עבור כל מיקום אפשרי שבו תיבת ה-bounding של הצורה נכנסת ללוח
            max_y = state.Board.shape[0] - shape_h
            max_x = state.Board.shape[1] - shape_w
            if max_y < 0 or max_x < 0:
                continue

            for y in range(0, max_y + 1):
                for x in range(0, max_x + 1):
                    if self.env.is_valid_move(state, block, (x, y)):
                        moves.append((block, (x, y)))
        return moves

    def get_after_states (self, moves, state):
        after_states = []
        for move in moves:
                block, pos = move
                grid_x, grid_y = pos
                
                # צור state חדש לאחר המהלך
                new_state = copy.deepcopy(state)
                self.env.fix_block_to_board(new_state, block, pos)
                self.env.check_and_explode_rows(new_state)
                
                # אם אין בלוקים ב-new_state, צור חדשים
                if not new_state.Blocks:
                    self.env.set_random_block(new_state)
                
                # קבל את ה-Q-value של ה-state הבא
                state_tensor = new_state.TensorState(new_state.Board)
                state_tensor = state_tensor.view(1, 8, 8)
                after_states.append(state_tensor)
        
        # Stack all tensors into a single tensor of shape [n, 1, 8, 8]
        after_tensors = torch.stack(after_states, dim=0)
        return after_tensors
    
    def move_to_action (self, best_move):
        block, (grid_x, grid_y) = best_move
            
        # המר קואורדינטות רשת לקואורדינטות פיקסלים
        pixel_x = self.GRID_ORIGIN_X + grid_x * self.GRID_SIZE
        pixel_y = self.GRID_ORIGIN_Y + grid_y * self.GRID_SIZE
        
        self.selected_block = block
        
        # החזר את הפעולה בפורמט שenv.move מצפה
        return (block, (pixel_x, pixel_y))
    
    def get_epsilon (self, epoch = 0):
        return 0.1