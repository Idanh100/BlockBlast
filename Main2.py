import pygame
from Graphics2 import Graphics
from State2 import State
import os

class Game:
    def __init__(self):
        pygame.init()
        info = pygame.display.get_desktop_sizes()[0]  # אם יש כמה מסכים – לוקח את הראשון
        width, height = info

        self.clock = pygame.time.Clock()
        self.clock.tick(60)  # מגביל ל־60 FPS
        
        self.State = State()
        self.Graphics = Graphics(width, height)
        
        self.run = True
        while (self.run):
            self.Graphics.draw_game(self.State)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False


            


if __name__ == "__main__":
    game = Game()