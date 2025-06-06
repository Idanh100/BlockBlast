import pygame
from Graphics import Graphics
from Environment import Environment
from HumanAgent import HumanAgent
from State import State
import sqlite3
import os

class Game:
    def __init__(self):
        pygame.init()
        self.init_database()

        info = pygame.display.get_desktop_sizes()[0]  # אם יש כמה מסכים – לוקח את הראשון
        width, height = info

        # Initialize Graphics first to get screen dimensions
        self.graphics = Graphics(width, height) 
        self.width, self.height = self.graphics.width, self.graphics.height
        
        # Initialize components
        self.human_agent = HumanAgent()
        self.state = State()
        self.state.human_agent = self.human_agent
        self.environment = Environment()
        
        # Update environment with grid settings from Graphics
        self.environment.grid_size = self.graphics.GRID_SIZE
        self.environment.grid_origin_x = self.graphics.GRID_ORIGIN_X
        self.environment.grid_origin_y = self.graphics.GRID_ORIGIN_Y
        
        # Game states
        self.MENU, self.PLAYING, self.GAME_OVER = "menu", "playing", "game_over"
        self.current_screen = self.MENU
        
        self.clock = pygame.time.Clock()
        self.running = True
    
    def init_database(self):
        if not os.path.exists('game_stats.db'):
            conn = sqlite3.connect('game_stats.db')
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    score INTEGER,
                    lines_cleared INTEGER,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            conn.close()
    
    def save_game_stats(self, score, lines_cleared):
        conn = sqlite3.connect('game_stats.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO game_stats (score, lines_cleared) VALUES (?, ?)', 
                      (score, lines_cleared))
        conn.commit()
        conn.close()
    
    def get_game_stats(self):
        conn = sqlite3.connect('game_stats.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT MAX(score) FROM game_stats')
        highest_score = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT AVG(score) FROM game_stats')
        avg_score = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT COUNT(*) FROM game_stats')
        games_played = cursor.fetchone()[0] or 0
        
        conn.close()
        return {
            'highest_score': highest_score,
            'avg_score': round(avg_score, 1),
            'games_played': games_played
        }
    
    def run(self):
        while self.running:
            # Handle different game screens
            if self.current_screen == self.MENU:
                self.run_menu()
            elif self.current_screen == self.PLAYING:
                self.run_game()
            elif self.current_screen == self.GAME_OVER:
                self.run_game_over()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
    
    def run_menu(self):
        action = self.human_agent.get_menu_action(self.graphics.draw_menu())
        if action == "start":
            self.state.reset()
            self.current_screen = self.PLAYING
        elif action == "quit":
            self.running = False
    
    def run_game(self):
        observation = self.environment.get_observation(self.state)
        
        action = self.human_agent.get_action(
            observation, 
            self.graphics.draw_game(
                self.state, 
                self.human_agent.highlighted_cells, 
                self.human_agent.highlight_color if self.human_agent.valid_placement else None
            )
        )
        
        reward, done = self.environment.step(self.state, action)
        
        if done:
            self.save_game_stats(self.state.score, self.state.lines_cleared)
            self.current_screen = self.GAME_OVER
    
    def run_game_over(self):
        stats = self.get_game_stats()
        action = self.human_agent.get_game_over_action(
            self.graphics.draw_game_over(self.state.score, stats)
        )
        
        if action == "menu":
            self.current_screen = self.MENU
        elif action == "quit":
            self.running = False

if __name__ == "__main__":
    Game().run()