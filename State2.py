import pygame
import random
import numpy as np

class State:
    def __init__(self):
        self.Board = np.zeros((8, 8))
        self.Blocks = (self.get_random_block(), self.get_random_block(), self.get_random_block())
        print(self.Board)
    
    def all_shapes(self):
        """Generate all possible block shapes for the game."""
        return {
            "square": [[1, 1], [1, 1]],
            "line2": [[1, 1]],
            "line3": [[1, 1, 1]],
            "line4": [[1, 1, 1, 1]],
            "line5": [[1, 1, 1, 1, 1]],
            "col2": [[1], [1]],
            "col3": [[1], [1], [1]],
            "col4": [[1], [1], [1], [1]],
            "col5": [[1], [1], [1], [1], [1]],
            "T": [[0, 1, 0], [1, 1, 1]],
            "T_inverted": [[1, 1, 1], [0, 1, 0]],
            "T_right": [[1, 0], [1, 1], [1, 0]],
            "T_left": [[0, 1], [1, 1], [0, 1]],
            "L": [[1, 0], [1, 0], [1, 1]],
            "L_flipped": [[0, 1], [0, 1], [1, 1]],
            "L_rotated": [[1, 1, 1], [1, 0, 0]],
            "L_rotated_flipped": [[1, 1, 1], [0, 0, 1]],
            "Z": [[1, 1, 0], [0, 1, 1]],
            "Z_vertical": [[0, 1], [1, 1], [1, 0]],
            "S": [[0, 1, 1], [1, 1, 0]],
            "S_vertical": [[1, 0], [1, 1], [0, 1]],
            "plus": [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
            "dot": [[1]],
            "small_square": [[1, 1], [1, 1]],
            "corner": [[1, 1], [1, 0]],
            "corner_flipped": [[1, 1], [0, 1]],
            "corner_rotated": [[0, 1], [1, 1]],
            "corner_rotated_flipped": [[1, 0], [1, 1]],
            "U": [[1, 0, 1], [1, 1, 1]],
            "U_rotated": [[1, 1], [1, 0], [1, 1]],
            "U_inverted": [[1, 1, 1], [1, 0, 1]],
            "U_rotated_flipped": [[1, 1], [0, 1], [1, 1]],
            "2x3": [[1, 1, 1], [1, 1, 1]],
            "3x3": [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
        }
    
    def get_random_block(self):
        """Get a random shape from all available shapes."""
        all_shapes = self.all_shapes()
        block = Block(random.choice(list(all_shapes.keys())))
        return block
    

class Block:
    def __init__(self, shape):
        self.shape = shape
        
        RED = (220, 70, 70)
        YELLOW = (240, 200, 50)
        ORANGE = (240, 130, 50)
        GREEN = (100, 200, 100)
        BLUE = (100, 100, 240)
        PURPLE = (180, 100, 240)
        colors = [RED, YELLOW, ORANGE, GREEN, BLUE, PURPLE]
        
        self.color = random.choice(colors)