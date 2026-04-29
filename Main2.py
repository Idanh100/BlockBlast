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
        """Check if close button was clicked in the given events."""
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
                        if restart_button.collidepoint(mouse_x, mouse_y):  # התחלת משחק חדש
                            env.reset()  # איפוס הסביבה
                            state = env.state  # קבלת המצב ההתחלתי
                            game_over = False  # איפוס מצב סיום המשחק
                        elif main_menu_button.collidepoint(mouse_x, mouse_y):  # חזרה לתפריט הראשי
                            menu_action = self.main_menu(graphics)  # הצגת התפריט הראשי
                            current_mode = menu_action  # עדכון המצב הנוכחי
                            if menu_action == "QUIT":  # אם המשתמש בחר לצאת
                                run = False
                            elif menu_action == "PLAY":  # אם המשתמש בחר לשחק
                                player = HumanAgent()  # יצירת שחקן אנושי
                                env.reset()  # איפוס הסביבה
                                state = env.state  # קבלת המצב ההתחלתי
                                game_over = False  # איפוס מצב סיום המשחק
                            elif menu_action == "AI_PLAY":  # אם המשתמש בחר ב-AI_PLAY
                                player = Ai_Agent(AI_PLAY=False)  # יצירת שחקן Ai_Agent
                                player.load_model(MODEL_PATH_TEMPLATE.format(DEFAULT_MODEL_NUMBER))  # טעינת המודל המאומן
                                env.reset()  # איפוס הסביבה
                                state = env.state  # קבלת המצב ההתחלתי
                                game_over = False  # איפוס מצב סיום המשחק
                            elif menu_action == "AI Play":  # אם המשתמש בחר באפשרות AI Play
                                player = Ai_Agent(AI_PLAY=False)  # יצירת שחקן Ai_Agent
                                player.load_model(MODEL_PATH_TEMPLATE.format(DEFAULT_MODEL_NUMBER))  # טעינת המודל המאומן
                                env.reset()  # איפוס הסביבה
                                state = env.state  # קבלת המצב ההתחלתי
                                game_over = False  # איפוס מצב סיום המשחק
            else:
                close_button_rect = graphics.draw_game(state, player.selected_block)
                pygame.display.flip()
                
                # בדוק אם לחצו על כפתור ה-Close
                if self.check_close_button(close_button_rect, events):
                    env.shutdown()
                    run = False
                    break
                
                # שלח את האירועים ל-agent
                action = player.get_action(state, events)  # קבלת פעולה מהשחקן עם האירועים
             ## the action will be the best move from ai agent
                if action == "QUIT":  # אם השחקן בחר לצאת
                    run = False
                elif action:  # אם השחקן ביצע פעולה
                    env.move(state, action)  # ביצוע הפעולה בסביבה
                    reward = env.Get_Reward_Args(action=action, state=env.state)
                    if isinstance(player, Ai_Agent):  # רק עבור סוכן AI
                        pygame.time.delay(AI_MOVE_DELAY)  # השהייה קצרה בין תורות של AI

                    #inside move convert to pixels be sure that human works the same
                    # move to pixel in environment
                    if env.is_game_over(state):  # בדיקה אם המשחק נגמר
                        game_over = True  # עדכון מצב סיום המשחק
                else:  # אם אין פעולה חוקית (למשל, אין מהלכים זמינים)
                    if env.is_game_over(state):  # בדיקה אם המשחק נגמר
                        game_over = True  # עדכון מצב סיום המשחק

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