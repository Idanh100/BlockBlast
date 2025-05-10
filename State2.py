import pygame
import random
import numpy as np

class State:
    def __init__(self):
        self.Board = np.zeros((8, 8))
        self.Blocks = ()
        self.score = 0  # אתחול הניקוד
        self.combo_count = 0  # מספר השורות ברצף
        self.turns_since_last_explosion = 0  # מספר התורות מאז הפיצוץ האחרון
        self.in_combo = False  # האם אנחנו ב-Combo

        print(self.Board)

