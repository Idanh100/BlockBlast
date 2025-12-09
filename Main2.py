import pygame
from Graphics2 import Graphics
from State2 import State
from Environment2 import Environment
from HumanAgent2 import HumanAgent
from Ai_Agent import Ai_Agent
import os

class Game:
    def __init__(self):        
        pass  # אתחול המחלקה Game (כרגע אין פעולות באתחול)

    def play(self):
        # אתחול רכיבי המשחק
        graphics = Graphics()  # מחלקה שאחראית על הגרפיקה
        env = Environment(State())  # יצירת הסביבה עם מצב התחלתי
        # player = HumanAgent()  # יצירת שחקן אנושי
        player = Ai_Agent()  # יצירת שחקן Ai_Agent
        run = True  # משתנה בוליאני שמנהל את לולאת המשחק

        # מסך פתיחה
        menu_action = self.main_menu(graphics)  # הצגת התפריט הראשי וקבלת פעולה מהמשתמש
        if menu_action == "QUIT":  # אם המשתמש בחר לצאת
            run = False
        elif menu_action == "TRAIN":  # אם המשתמש בחר באפשרות Train AI
            run = False  # סיום המשחק

        # אתחול הסביבה והמצב
        env.reset()  # איפוס הסביבה
        state = env.state  # קבלת המצב ההתחלתי
        game_over = False  # משתנה שמנהל את מצב סיום המשחק

        # לולאת המשחק הראשית
        while run:
            if game_over:  # אם המשחק נגמר
                # הדפסת הניקוד של המשתמש
                print(f"Game Over! Your Score: {state.score}")

                # הצגת מסך Game Over
                restart_button, main_menu_button = graphics.draw_game_over(state)
                for event in pygame.event.get():  # טיפול באירועים
                    if event.type == pygame.QUIT:  # אם המשתמש סגר את החלון
                        run = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:  # אם המשתמש לחץ על העכבר
                        mouse_x, mouse_y = event.pos  # קבלת מיקום הלחיצה
                        if restart_button.collidepoint(mouse_x, mouse_y):  # התחלת משחק חדש
                            env.reset()  # איפוס הסביבה
                            state = env.state  # קבלת המצב ההתחלתי
                            game_over = False  # איפוס מצב סיום המשחק
                        elif main_menu_button.collidepoint(mouse_x, mouse_y):  # חזרה לתפריט הראשי
                            menu_action = self.main_menu(graphics)  # הצגת התפריט הראשי
                            if menu_action == "QUIT":  # אם המשתמש בחר לצאת
                                run = False
                            elif menu_action == "PLAY":  # אם המשתמש בחר לשחק
                                env.reset()  # איפוס הסביבה
                                state = env.state  # קבלת המצב ההתחלתי
                                game_over = False  # איפוס מצב סיום המשחק
                            elif menu_action == "TRAIN":  # אם המשתמש בחר באפשרות Train AI
                                run = False  # סיום המשחק
            else:  # אם המשחק ממשיך
                graphics.draw_game(state, player.selected_block)  # ציור מצב המשחק הנוכחי
                pygame.display.flip()  # עדכון המסך
                action = player.get_action(state)  # קבלת פעולה מהשחקן
                if action == "QUIT":  # אם השחקן בחר לצאת
                    run = False
                elif action:  # אם השחקן ביצע פעולה
                    env.move(state, action)  # ביצוע הפעולה בסביבה
                    if env.is_game_over(state):  # בדיקה אם המשחק נגמר
                        game_over = True  # עדכון מצב סיום המשחק
                for event in pygame.event.get():  # טיפול באירועים
                    if event.type == pygame.QUIT:  # אם המשתמש סגר את החלון
                        run = False

    def main_menu(self, graphics):
        """
        Display the main menu and handle button clicks.
        """
        while True:
            # ציור התפריט הראשי
            play_button, train_button, quit_button = graphics.draw_main_menu()

            for event in pygame.event.get():  # טיפול באירועים
                if event.type == pygame.QUIT:  # אם המשתמש סגר את החלון
                    return "QUIT"
                elif event.type == pygame.MOUSEBUTTONDOWN:  # אם המשתמש לחץ על העכבר
                    mouse_x, mouse_y = event.pos  # קבלת מיקום הלחיצה
                    if play_button.collidepoint(mouse_x, mouse_y):  # אם המשתמש לחץ על כפתור Play
                        return "PLAY"
                    elif train_button.collidepoint(mouse_x, mouse_y):  # אם המשתמש לחץ על כפתור Train AI
                        return "TRAIN"
                    elif quit_button.collidepoint(mouse_x, mouse_y):  # אם המשתמש לחץ על כפתור Quit
                        return "QUIT"


if __name__ == "__main__":
    game = Game()  # יצירת אובייקט של המשחק
    game.play()  # התחלת המשחק