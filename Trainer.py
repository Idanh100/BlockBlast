import pygame
from Graphics2 import Graphics
from State2 import State
from Environment2 import Environment
from HumanAgent2 import HumanAgent
from Ai_Agent2 import Ai_Agent
from Replay_Buffer import ReplayBuffer
from Model import DQN
import copy
import torch
import os

class Game:
    def __init__(self):        
        pass  # אתחול המחלקה Game (כרגע אין פעולות באתחול)

    def train(self): 
        # אתחול רכיבי המשחק
        graphics = Graphics()  # מחלקה שאחראית על הגרפיקה
        env = Environment(State())  # יצירת הסביבה עם מצב התחלתי
        run = True  # משתנה בוליאני שמנהל את לולאת המשחק

        # אתחול הסביבה והמצב

        game_over = False  # משתנה שמנהל את מצב סיום המשחק
        player = Ai_Agent()
        player_hat = Ai_Agent()
        player_hat.model.load_state_dict(player.model.state_dict())
        batch_size = 50
        best_score = 0
        buffer = ReplayBuffer(path=None)
        learning_rate = 0.00001
        epochs = 200000
        start_epoch = 0
        C = 3
        loss = torch.tensor(0)
        avg = 0
        scores, losses, avg_score = [], [], []
        optim = torch.optim.Adam(player.model.parameters(), lr=learning_rate)
        # scheduler = torch.optim.lr_scheduler.StepLR(optim,100000, gamma=0.50)
        scheduler = torch.optim.lr_scheduler.MultiStepLR(optim,[5000*1000, 10000*1000, 15000*1000], gamma=0.5)
        step = 0
            
        for epoch in range(epochs):
            env.reset()  # איפוס הסביבה
            state = env.state.copy()  # קבלת המצב ההתחלתי
            # לולאת המשחק הראשית
            while True:
                for event in pygame.event.get():  # טיפול באירועים
                    if event.type == pygame.QUIT:  # אם המשתמש סגר את החלון
                        run = False
                        break
                
                # אם המשחק ממשיך
                graphics.draw_game(env.state, player.selected_block)  # ציור מצב המשחק הנוכחי
                pygame.display.flip()  # עדכון המסך
                    
                action, after_state_tensor = player.get_action_train(state=env.state, epoch=epochs)
                env.move(action=action, state=env.state)
                done = env.is_game_over(env.state)
                reward = env.Get_Reward_Args(action=action, state=env.state)
                print("Reward:", reward)
                next_state = env.state.copy()
                buffer.push(state, action, after_state_tensor, torch.tensor(reward, dtype=torch.float32), 
                            next_state, torch.tensor(done, dtype=torch.float32))
                if done:
                    # best_score = max(best_score, env.score)
                    break

                if len(buffer) < 5000000:
                    continue

                states, actions, rewards, next_states, dones = buffer.sample(batch_size)
                Q_values = player.Q(states, actions)
                next_actions, Q_hat_Values = player_hat.get_Actions_Values(next_states)

                loss = player.model.loss(Q_values, rewards, Q_hat_Values, dones)
                loss.backward()
                optim.step()
                optim.zero_grad()
                scheduler.step()

                if epochs % C == 0:
                    player_hat.model.load_state_dict(player.model.state_dict())


                action = player.get_action(state)  # קבלת פעולה מהשחקן
                ## the action will be the best move from ai agent
                env.move(state, action)  # ביצוע הפעולה בסביבה
                    #inside move convert to pixels be sure that human works the same
                    # move to pixel in environment
                if env.is_game_over(state):  # בדיקה אם המשחק נגמר
                    print(epochs, state.score)
                    env.reset()  # איפוס הסביבה
                    state = env.state  # קבלת המצב ההתחלתי
                    game_over = True  # איפוס מצב סיום המשחק
                    break
                    
                


if __name__ == "__main__":
    game = Game()  # יצירת אובייקט של המשחק
    game.train()  # התחלת המשחק