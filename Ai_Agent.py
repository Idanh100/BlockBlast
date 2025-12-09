import pygame
import torch
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
        # קבל את כל המהלכים האפשריים
        moves = self.env.GetAllPossibleMoves(state)
        
        if not moves:
            return None
        
        # בחר מהלך עם ה-Q-value הגבוה ביותר
        best_move = None
        best_q_value = float('-inf')
        
        for move in moves:
            name, shape, pos = move
            next_states = self.env.AfterState(state, [move])
            next_state = next_states[0]
            
            # קבל את ה-Q-value של ה-state הבא
            state_tensor = next_state.TensorState(next_state.Board)
            state_tensor = state_tensor.view(1, 1, 8, 8)
            
            with torch.no_grad():  # אל תחשב gradients בהערכה
                q_value = self.model(state_tensor).item()
            
            # בחר את המהלך עם ה-Q-value הגבוה ביותר
            if q_value > best_q_value:
                best_q_value = q_value
                best_move = move
        
        if best_move:
            name, shape, pos = best_move
            grid_x, grid_y = pos
            
            # המר קואורדינטות רשת לקואורדינטות פיקסלים
            pixel_x = self.GRID_ORIGIN_X + grid_x * self.GRID_SIZE
            pixel_y = self.GRID_ORIGIN_Y + grid_y * self.GRID_SIZE
            
            # יצור Block דמה
            dummy_block = Block(shape, pygame.Rect(pixel_x, pixel_y, 0, 0), 1)
            self.selected_block = dummy_block
            
            # החזר את הפעולה בפורמט שenv.move מצפה
            return (dummy_block, (pixel_x, pixel_y))
        
        return None