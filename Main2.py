import pygame
from Graphics2 import Graphics
from State2 import State
from Environment2 import Environment
from HumanAgent2 import HumanAgent
from Ai_Agent2 import Ai_Agent
import os
from CONSTANTS import *

class Game:
    def __init__(self):        
        pass
    
    def check_close_button(self, close_button_rect, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and close_button_rect.collidepoint(event.pos):
                return True
        return False

    def play(self):
        graphics = Graphics()
        env = Environment(State())
        run = True

        menu_action = self.main_menu(graphics)
        current_mode = menu_action
        if menu_action == "QUIT":
            run = False
        elif menu_action == "PLAY":
            player = HumanAgent()
        elif menu_action == "AI_PLAY":
            player = Ai_Agent(train=False)
            player.load_model(MODEL_PATH_TEMPLATE.format(DEFAULT_MODEL_NUMBER))

        env.reset()
        state = env.state
        game_over = False


        while run:
            events = pygame.event.get()
            
            for event in events:
                if event.type == pygame.QUIT:
                    env.shutdown()
                    run = False
                    break
            
            if not run:
                break
            
            if game_over:
                restart_button, main_menu_button = graphics.draw_game_over(state)
                for event in events:
                    if event.type == pygame.QUIT:
                        run = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = event.pos
                        if restart_button.collidepoint(mouse_x, mouse_y):
                            env.reset()
                            state = env.state
                            game_over = False
                        elif main_menu_button.collidepoint(mouse_x, mouse_y):
                            menu_action = self.main_menu(graphics)
                            current_mode = menu_action
                            if menu_action == "QUIT":
                                run = False
                            elif menu_action == "PLAY":
                                player = HumanAgent()
                                env.reset()
                                state = env.state
                                game_over = False
                            elif menu_action == "AI_PLAY":
                                player = Ai_Agent(AI_PLAY=False)
                                player.load_model(MODEL_PATH_TEMPLATE.format(DEFAULT_MODEL_NUMBER))
                                env.reset()
                                state = env.state
                                game_over = False
                            elif menu_action == "AI Play":
                                player = Ai_Agent(AI_PLAY=False)
                                player.load_model(MODEL_PATH_TEMPLATE.format(DEFAULT_MODEL_NUMBER))
                                env.reset()
                                state = env.state
                                game_over = False
            else:
                close_button_rect = graphics.draw_game(state, player.selected_block)
                pygame.display.flip()
                
                if self.check_close_button(close_button_rect, events):
                    env.shutdown()
                    run = False
                    break
                
                action = player.get_action(state, events)
                if action == "QUIT":
                    run = False
                elif action:
                    env.move(state, action)
                    reward = env.Get_Reward_Args(action=action, state=env.state)
                    if isinstance(player, Ai_Agent):
                        pygame.time.delay(AI_MOVE_DELAY)

                    if env.is_game_over(state):
                        game_over = True
                else:
                    if env.is_game_over(state):
                        game_over = True

    def main_menu(self, graphics):
        while True:
            play_button, AI_PLAY_button, quit_button = graphics.draw_main_menu()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    if play_button.collidepoint(mouse_x, mouse_y):
                        return "PLAY"
                    elif AI_PLAY_button.collidepoint(mouse_x, mouse_y):
                        return "AI_PLAY"
                    elif quit_button.collidepoint(mouse_x, mouse_y):
                        return "QUIT"


if __name__ == "__main__":
    game = Game()
    game.play()