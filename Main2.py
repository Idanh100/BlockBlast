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
        player = HumanAgent()
        run = True

        # מסך פתיחה
        menu_action = self.main_menu(graphics)
        if menu_action == "QUIT":
            run = False
        elif menu_action == "TRAIN":
            print("Train AI selected. (Feature not implemented yet)")
            run = False  # סגור את המשחק או החלף למסך אחר

        env.reset()
        state = env.state
        game_over = False

        while run:
            if game_over:
                restart_button, main_menu_button = graphics.draw_game_over(state)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = event.pos
                        if restart_button.collidepoint(mouse_x, mouse_y):  # התחלת משחק חדש
                            env.reset()
                            state = env.state
                            game_over = False
                        elif main_menu_button.collidepoint(mouse_x, mouse_y):  # חזרה לתפריט הראשי
                            menu_action = self.main_menu(graphics)
                            if menu_action == "QUIT":
                                run = False
                            elif menu_action == "PLAY":
                                env.reset()
                                state = env.state
                                game_over = False
                            elif menu_action == "TRAIN":
                                print("Train AI selected. (Feature not implemented yet)")
                                run = False
            else:
                graphics.draw_game(state, player.selected_block)
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

    def main_menu(self, graphics):
        """
        Display the main menu and handle button clicks.
        """
        while True:
            play_button, train_button, quit_button = graphics.draw_main_menu()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    if play_button.collidepoint(mouse_x, mouse_y):
                        return "PLAY"
                    elif train_button.collidepoint(mouse_x, mouse_y):
                        return "TRAIN"
                    elif quit_button.collidepoint(mouse_x, mouse_y):

                        return "QUIT"


if __name__ == "__main__":
    game = Game()
    game.play()