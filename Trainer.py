import pygame
from Graphics2 import Graphics
import Model
from State2 import State
from Environment2 import Environment
from HumanAgent2 import HumanAgent
from Ai_Agent2 import Ai_Agent
from Replay_Buffer import ReplayBuffer
from Model import DQN
import copy
import torch
import wandb
import os
from CONSTANTS import *

class Game:
    def __init__(self):        
        pass

    def train(self): 
        graphics = Graphics()
        env = Environment(State())
        run = True
        num = DEFAULT_MODEL_NUMBER
        Buffer_Path = BUFFER_PATH_TEMPLATE.format(num)
        Model_Path = MODEL_PATH_TEMPLATE.format(num)

        game_over = False
        player = Ai_Agent()
        player_hat = Ai_Agent()
        player_hat.model.load_state_dict(player.model.state_dict())
        batch_size = BATCH_SIZE
        best_score = 0
        buffer = ReplayBuffer(path=None)
        learning_rate = LEARNING_RATE
        epochs = NUM_EPOCHS
        start_epoch = 0
        C = NETWORK_UPDATE_FREQUENCY
        epsilon_decay = EPSILON_DECAY
        loss = torch.tensor(0)
        avg = 0
        scores, losses, avg_score = [], [], []
        optim = torch.optim.Adam(player.model.parameters(), lr=learning_rate)
        scheduler = torch.optim.lr_scheduler.MultiStepLR(optim,[m*1000 for m in LR_SCHEDULER_MILESTONES], gamma=LR_SCHEDULER_GAMMA)
        step = 0
        episode_rewards = []
        
        wandb_run = wandb.init(
            project=WANDB_PROJECT,
            resume=False, 
            id=f'Block_Blast_{num}',
            config={
                "name": f"Block_Blast_{num}",
                "checkpoint_path": Model_Path,
                "buffer_path": Buffer_Path,
                "learning_rate": learning_rate,
                "architecture": "FNN 128, 258, 512, 128, 64, 4",
                "schedule": f"Milestones: {LR_SCHEDULER_MILESTONES} gamma={LR_SCHEDULER_GAMMA}",
                "epochs": epochs,
                "start_epoch": start_epoch,
                "epsilon_decay": epsilon_decay,
                "gamma": GAMMA,
                "batch_size": batch_size,
                "C": C,
            },
        )
        torch.save(player.model, Model_Path)

        env.reset()
            
        for epoch in range(epochs):
            state = env.state.copy()
            episode_reward = 0
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        close_button_rect = graphics.get_close_button_rect()
                        if close_button_rect.collidepoint(event.pos):
                            pygame.quit()
                            return
                
                graphics.draw_game(env.state, player.selected_block)
                pygame.display.flip()
                    
                action, after_state_tensor = player.get_action_train(state=env.state, epoch=epoch)
                env.move(action=action, state=env.state)
                done = env.is_game_over(env.state)
                reward = env.Get_Reward_Args(action=action, state=env.state)
                episode_reward += reward
                next_state = env.state.copy()
                
                state_tensor = state.TensorState(state.Board).view(1, 8, 8)
                next_state_tensor = next_state.TensorState(next_state.Board).view(1, 8, 8)
                
                block, (pixel_x, pixel_y) = action
                action_tensor = torch.tensor([pixel_x, pixel_y], dtype=torch.float32).view(1, 2)
                reward_tensor = torch.tensor(reward, dtype=torch.float32).view(1, 1)
                done_tensor = torch.tensor(done, dtype=torch.float32).view(1, 1)
                
                buffer.push(state_tensor, action_tensor, reward_tensor, 
                            next_state_tensor, done_tensor)
                
                state = next_state
                
                if done:
                    scores.append(env.state.score)
                    episode_rewards.append(episode_reward)
                    wandb.log({
                        "episode_reward": episode_reward,
                        "score": env.state.score,
                        "epoch": epoch,
                        "step": step,
                    })
                    break
                
                if len(buffer) < MIN_BUFFER_SIZE_FOR_TRAINING:
                    continue

                states, actions, rewards, next_states, dones = buffer.sample(batch_size)
                Q_values = player.Q(states, actions)
                next_actions, Q_hat_Values = player_hat.get_Actions_Values(next_states)

                loss = player.model.loss(Q_values, rewards, Q_hat_Values, dones)
                losses.append(loss.item())
                wandb.log({"loss": loss.item(), "step": step})
                
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
                wandb.log({
                    "avg_score": avg_score,
                    "avg_reward": avg_reward,
                    "avg_loss": avg_loss,
                    "epsilon": epsilon,
                    "best_score": max(scores) if scores else 0,
                    "REWARD_EXPLODE": REWARD_EXPLODE,
                    "REWARD_SQUARES_PER_BLOCK": REWARD_SQUARES_PER_BLOCK,
                    "REWARD_SQUARES_IN_SAME_ROW_OR_COL": REWARD_SQUARES_IN_SAME_ROW_OR_COL
                })
                torch.save(player.model.state_dict(), Model_Path)
                torch.save(buffer, "Data/Buffer.pth")
            
            
            
            env.reset()       
        try:
            wandb_run.finish()
        except Exception:
            pass

if __name__ == "__main__":
    game = Game()
    game.train()