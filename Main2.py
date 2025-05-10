import pygame
from Graphics2 import Graphics
from State2 import State
from Environment2 import Environment
from HumanAgent2 import HumanAgent
import os

class Game:
    def __init__(self):        
       pass

    def play(self):
        graphics = Graphics()
        env = Environment(State())
        env.reset()
        player = HumanAgent()
        run = True
        state = env.state
        game_over = False

        while run:
            if game_over:
                graphics.draw_game_over(state)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:  # התחלת משחק חדש
                            env.reset()
                            state = env.state
                            game_over = False
                        elif event.key == pygame.K_q:  # יציאה מהמשחק
                            run = False
            else:
                graphics.draw_game(state)
                pygame.display.flip()
                action = player.get_action(state)
                if action == "QUIT":
                    run = False
                elif action:
                    env.move(state, action)
                    if env.is_game_over(state):  # בדיקה אם המשחק נגמר
                        game_over = True
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False


if __name__ == "__main__":
    game = Game()
    game.play()