import numpy as np
import torch
import copy

class State:
    def __init__(self):
        self.Board = np.zeros((8, 8))
        self.Blocks = ()
        self.score = 0
        self.combo_count = 0
        self.turns_since_last_explosion = 0
        self.in_combo = False

    def TensorState(self, Board):
        tensor_state = torch.tensor(Board, dtype=torch.float32)        
        return tensor_state
    
    def copy(self):
        return copy.deepcopy(self)
        

