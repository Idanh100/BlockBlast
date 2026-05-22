import numpy as np
import torch
import copy

class State:
    def __init__(self):
        self.Board = np.zeros((8, 8)) # הלוח
        self.Blocks = () # בלוקים זמינים
        self.score = 0 # ניקוד
        self.combo_count = 0 # מספר הקומבו
        self.turns_since_last_explosion = 0 # כמה תורות היו מאז  הפיצוץ האחרון
        self.in_combo = False # האם השחקן בקומבו כרגע

    def TensorState(self, Board): # PyTorch ממיר את הלוח למבנה טנסור של 
        tensor_state = torch.tensor(Board, dtype=torch.float32)        
        return tensor_state
    
    def copy(self): # יוצר עותק מדויק של המצב הנוכחי
        return copy.deepcopy(self)
        

