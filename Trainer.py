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
        epochs = 20000
        start_epoch = 0
        C = 3
        loss = torch.tensor(0)
        avg = 0
        scores, losses, avg_score = [], [], []
        optim = torch.optim.Adam(player.model.parameters(), lr=learning_rate)
        # scheduler = torch.optim.lr_scheduler.StepLR(optim,100000, gamma=0.50)
        scheduler = torch.optim.lr_scheduler.MultiStepLR(optim,[5000*1000, 10000*1000, 15000*1000], gamma=0.5)
        step = 0
        episode_rewards = []  # Track rewards for each episode
        
        # Initialize environment once
        env.reset()
            
        for epoch in range(epochs):
            state = env.state.copy()
            episode_reward = 0  # Track reward for this episode
            # לולאת המשחק הראשית - משחק אחד
            while True:
                for event in pygame.event.get():  # טיפול באירועים
                    if event.type == pygame.QUIT:  # אם המשתמש סגר את החלון
                        pygame.quit()
                        return
                
                # אם המשחק ממשיך
                graphics.draw_game(env.state, player.selected_block)  # ציור מצב המשחק הנוכחי
                pygame.display.flip()  # עדכון המסך
                    
                action, after_state_tensor = player.get_action_train(state=env.state, epoch=epoch)
                env.move(action=action, state=env.state)
                done = env.is_game_over(env.state)
                reward = env.Get_Reward_Args(action=action, state=env.state)
                episode_reward += reward
                next_state = env.state.copy()
                
                # Convert states to tensors for storage in buffer
                state_tensor = state.TensorState(state.Board).view(1, 8, 8)
                next_state_tensor = next_state.TensorState(next_state.Board).view(1, 8, 8)
                
                # Extract action coordinates and convert to tensor
                block, (pixel_x, pixel_y) = action
                action_tensor = torch.tensor([pixel_x, pixel_y], dtype=torch.float32).view(1, 2)
                reward_tensor = torch.tensor(reward, dtype=torch.float32).view(1, 1)
                done_tensor = torch.tensor(done, dtype=torch.float32).view(1, 1)
                
                buffer.push(state_tensor, action_tensor, reward_tensor, 
                            next_state_tensor, done_tensor)
                
                # Update state for next step
                state = next_state
                
                if done:
                    # End of episode - save metrics
                    scores.append(env.state.score)
                    episode_rewards.append(episode_reward)
                    break
                
                if len(buffer) < 5000:
                    continue

                states, actions, rewards, next_states, dones = buffer.sample(batch_size)
                Q_values = player.Q(states, actions)
                next_actions, Q_hat_Values = player_hat.get_Actions_Values(next_states)

                loss = player.model.loss(Q_values, rewards, Q_hat_Values, dones)
                losses.append(loss.item())
                
                # Debug: print values if loss is 0
                if loss.item() == 0:
                    print(f"\n!!! ZERO LOSS DETECTED !!!")
                    print(f"Q_values sample: {Q_values[0].item():.6f}")
                    print(f"Q_hat_Values sample: {Q_hat_Values[0].item():.6f}")
                    print(f"Rewards sample: {rewards[0].item():.6f}")
                    print(f"Dones sample: {dones[0].item():.6f}")
                    print(f"Target Q sample: {(rewards[0] + 0.99 * Q_hat_Values[0] * (1 - dones[0])).item():.6f}")
                
                loss.backward()
                optim.step()
                optim.zero_grad()
                scheduler.step()

                if epoch % C == 0:
                    player_hat.model.load_state_dict(player.model.state_dict())
                    
                step += 1
            
            # Print progress every 100 episodes
            if epoch % 100 == 0 and epoch > 0:
                avg_score = sum(scores[-100:]) / 100
                avg_loss = sum(losses[-100:]) / len(losses[-100:]) if losses else 0
                avg_reward = sum(episode_rewards[-100:]) / 100
                epsilon = player.get_epsilon(epoch)
                print(f"\n=== Epoch {epoch}/{epochs} ===")
                print(f"Avg Score (last 100): {avg_score:.2f}")
                print(f"Avg Reward (last 100): {avg_reward:.2f}")
                print(f"Avg Loss (last 100): {avg_loss:.6f}")
                print(f"Epsilon: {epsilon:.4f}")
                print(f"Buffer Size: {len(buffer)}")
                print(f"Best Score: {max(scores) if scores else 0}")
            
            # After episode ends, reset for next episode
            env.reset()
                    
                


if __name__ == "__main__":
    game = Game()  # יצירת אובייקט של המשחק
    game.train()  # התחלת המשחק