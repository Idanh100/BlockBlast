import pygame
from Graphics2 import Graphics
from State2 import State
from Environment2 import Environment
from HumanAgent2 import HumanAgent
from Ai_Agent2 import Ai_Agent
from CONSTANTS import *

class Game:
    def __init__(self):        
        pass
    
    def check_close_button(self, close_button_rect, events): # בודק אם המשתמק לחץ על הכפתור שסוגר את המשחק
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and close_button_rect.collidepoint(event.pos):
                return True
        return False

    def play(self):
        # אתחול הגרפיקה וסביבת המשחק
        graphics = Graphics()
        env = Environment(State())
        run = True

        # פותח תפריט ראשי ומגדיר את מצב השחקן לפי מה שהמשתמש בוחר
        menu_action = self.main_menu(graphics)
        if menu_action == "QUIT":
            run = False
        elif menu_action == "PLAY":
            # שחקן אנושי
            player = HumanAgent()
        elif menu_action == "AI_PLAY":
            # CONSTANTSשחקן בינה מלאכותית - נטען מודל של מספר שמור ב
            player = Ai_Agent(train=False) # תפריט ראשי
            player.load_model(MODEL_PATH_TEMPLATE.format(DEFAULT_MODEL_NUMBER))

        env.reset()
        state = env.state
        game_over = False

        # לולאת המשחק הראשית
        while run:
            events = pygame.event.get()

            # טיפול בסגירת החלון
            for event in events:
                if event.type == pygame.QUIT:
                    env.shutdown()
                    run = False
                    break

            if not run:
                break

            if game_over: # Game Over תפריט
                restart_button, main_menu_button = graphics.draw_game_over(state)
                for event in events:
                    if event.type == pygame.QUIT:
                        run = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_x, mouse_y = event.pos
                        if restart_button.collidepoint(mouse_x, mouse_y):
                            # אתחול משחק מחדש
                            env.reset()
                            state = env.state
                            game_over = False
                        elif main_menu_button.collidepoint(mouse_x, mouse_y):
                            # חזרה לתפריט הראשי ובחירה מחודשת של מצב המשחק
                            menu_action = self.main_menu(graphics)
                            if menu_action == "QUIT":
                                run = False
                            elif menu_action == "PLAY":
                                player = HumanAgent()
                                env.reset()
                                state = env.state
                                game_over = False
                            elif menu_action == "AI_PLAY":
                                player = Ai_Agent(train=False) # אחרי משחק
                                player.load_model(MODEL_PATH_TEMPLATE.format(DEFAULT_MODEL_NUMBER))
                                env.reset()
                                state = env.state
                                game_over = False
            else:
                # ציור המשחק
                close_button_rect = graphics.draw_game(state, player.selected_block)
                pygame.display.flip()

                if self.check_close_button(close_button_rect, events):
                    env.shutdown()
                    run = False
                    break

                # מקבל את הפעולה מהשחקן
                action = player.get_action(state, events)
                if action == "QUIT":
                    run = False
                elif action:
                    # העברת הפעולה לסביבה ועיבוד התוצאה
                    env.move(state, action)
                    reward = env.Get_Reward_Args(action=action, state=env.state)
                    if isinstance(player, Ai_Agent): # מוסיף לסוכן בינה מלאכותית דיליי בין כל מהלך
                        pygame.time.delay(AI_MOVE_DELAY)

                    if env.is_game_over(state):
                        game_over = True
                else:
                    # אין פעולה (השחקן לא עשה כלום)
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