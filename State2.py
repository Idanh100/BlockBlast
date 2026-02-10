import numpy as np
import torch
import copy

class State:
    def __init__(self):
        self.Board = np.zeros((8, 8))
        self.Blocks = ()
        self.score = 0  # אתחול הניקוד
        self.combo_count = 0  # מספר השורות ברצף
        self.turns_since_last_explosion = 0  # מספר התורות מאז הפיצוץ האחרון
        self.in_combo = False  # האם אנחנו ב-Combo

    def TensorState(self, Board): #בונה state בtensor 
        tensor_state = torch.tensor(Board, dtype=torch.float32)        
        return tensor_state
    
    def copy(self):
        return copy.deepcopy(self)
        

