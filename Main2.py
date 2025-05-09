import pygame
from Graphics2 import Graphics
from State2 import State
from Environment2 import Environment
from HumanAgent2 import HumanAgent
import os

class Game:
    def __init__(self):        
       pass

    def play (self):
        graphics = Graphics()
        env = Environment(State())
        env.reset()
        player = HumanAgent()
        run = True
        state = env.state
        while (run):
            graphics.draw_game(state)
            pygame.display.flip()
            action = player.get_action(state)
            if action == "QUIT":
                run = False
            elif action:
                env.move(state, action)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False


            


if __name__ == "__main__":
    game = Game()
    game.play()