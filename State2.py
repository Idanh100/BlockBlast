import pygame
import random
import numpy as np

class State:
    def __init__(self):
        self.Board = np.zeros((8, 8))
        self.Blocks = ()
        print(self.Board)

    