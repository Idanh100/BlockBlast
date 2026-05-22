import pygame
from Graphics2 import Graphics
from State2 import State
from Environment2 import Environment
from Ai_Agent2 import Ai_Agent
from Replay_Buffer import ReplayBuffer
import torch
import wandb
from CONSTANTS import *

class Game:
    def __init__(self):        
        pass

    def train(self):
        graphics = Graphics()
        env = Environment(State())  # יצירת הסביבה עם מצב התחלתי
        num = DEFAULT_MODEL_NUMBER  # מספר המודל
        Buffer_Path = BUFFER_PATH_TEMPLATE.format(num)  # Bufferנתיב לשמירת ה
        Model_Path = MODEL_PATH_TEMPLATE.format(num)  # נתיב לשמירת המודל

        player = Ai_Agent()  # סוכן בינה מלאכותית ראשי
        player_hat = Ai_Agent()  # מודל יעד (target network)
        player_hat.model.load_state_dict(player.model.state_dict())  # העתקת פרמטרים למודל היעד
        batch_size = BATCH_SIZE  # גודל אוסף החוויות לאימון
        buffer = ReplayBuffer(path=None)  # יוצר Buffer חדש לצורך שמירת חוויות במהלך האימון
        learning_rate = LEARNING_RATE  # שיעור למידה לשיפועי האופטימייזר
        epochs = NUM_EPOCHS  # מספר חזרות על לולאת האימון
        start_epoch = 0  # מספר החזרה להתחלה, שימושי אם רוצים להמשיך אימון קיים
        C = NETWORK_UPDATE_FREQUENCY  # תדירות עדכון ה-target network
        epsilon_decay = EPSILON_DECAY  # קצב הקטנת האפסילון
        loss = torch.tensor(0)  # ערך השגיאה
        scores, losses, avg_score = [], [], []  # רשימות לשמירת סטטיסטיקה
        optim = torch.optim.Adam(player.model.parameters(), lr=learning_rate)  # אופטימייזר Adam
        scheduler = torch.optim.lr_scheduler.MultiStepLR(optim,[m*1000 for m in LR_SCHEDULER_MILESTONES], gamma=LR_SCHEDULER_GAMMA)  # בכל מספר צעדים, להוריד את הlearning rate פי gamma
        step = 0  # סופר צעדים 
        episode_rewards = []  # רשימת תגמולים לכל שמירה
        
        wandb_run = wandb.init(  # אתחול ריצה ב wandb
            project=WANDB_PROJECT,
            resume=False, 
            id=f'Block_Blast_{num}', # מספר השמירה
            config={  # wandbכל הערכים האלה ישמרו כפרמטרים ב
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
                "REWARD_EXPLODE": REWARD_EXPLODE,
                "REWARD_SQUARES_PER_BLOCK": REWARD_SQUARES_PER_BLOCK,
                "REWARD_SQUARES_IN_SAME_ROW_OR_COL": REWARD_SQUARES_IN_SAME_ROW_OR_COL,
                "batch_size": batch_size,
                "C": C,
            },
        )
        torch.save(player.model, Model_Path)  # שמירת המודל ההתחלתי

        env.reset()  # אתחול הסביבה
            
        for epoch in range(epochs):  # לולאה על אפוקים
            state = env.state.copy()  # העתקת מצב התחלתי
            episode_reward = 0  # איפוס תגמול לריצה הנוכחית
            while True:  # לולאת צעדים בתוך ריצה
                for event in pygame.event.get():  # טיפול באירועי pygame
                    if event.type == pygame.QUIT:  # אם סוגרים את החלון
                        pygame.quit()  # יציאה מ-pygame
                        return  # סיום הפונקציה
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:  # לחיצה בעכבר
                        close_button_rect = graphics.get_close_button_rect()  # מיקום כפתור סגירה
                        if close_button_rect.collidepoint(event.pos):  # בדיקה אם נלחץ הכפתור
                            pygame.quit()  # יציאה מ-pygame
                            return  # סיום הפונקציה
                
                graphics.draw_game(env.state, player.selected_block)  # ציור המשחק על המסך
                pygame.display.flip()  # רענון התצוגה
                    
                action, after_state_tensor = player.get_action_train(state=env.state, epoch=epoch)  # קבלת פעולה מה-agent
                env.move(action=action, state=env.state)  # ביצוע המהלך בסביבה
                done = env.is_game_over(env.state)  # בדיקה אם המשחק הסתיים
                reward = env.Get_Reward_Args(action=action, state=env.state)  # חישוב תגמול עבור המהלך
                episode_reward += reward  # עדכון תגמול הריצה
                next_state = env.state.copy()  # מצב לאחר המהלך
                
                state_tensor = state.TensorState(state.Board).view(1, 8, 8)  # המרת מצב לטנסור כניסה
                next_state_tensor = next_state.TensorState(next_state.Board).view(1, 8, 8)  # טנסור למצב הבא
                
                block, (pixel_x, pixel_y) = action  # פירוק הפעולה לרכיבים
                action_tensor = torch.tensor([pixel_x, pixel_y], dtype=torch.float32).view(1, 2)  # המרת פעולה לטנסור
                reward_tensor = torch.tensor(reward, dtype=torch.float32).view(1, 1)  # טנסור תגמול
                done_tensor = torch.tensor(done, dtype=torch.float32).view(1, 1)  # טנסור דגל סיום
                
                buffer.push(state_tensor, action_tensor, reward_tensor, 
                            next_state_tensor, done_tensor)  # דחיפת הדוגמה ל-buffer
                
                state = next_state  # עדכון המצב הנוכחי
                
                if done:  # טיפול בסיום ריצה
                    scores.append(env.state.score)  # שמירת הציון ברשימה
                    episode_rewards.append(episode_reward)  # שמירת תגמול הריצה
                    wandb.log({  # רישום למדדים ב-wandb
                        "episode_reward": episode_reward,
                        "score": env.state.score,
                        "epoch": epoch,
                        "step": step,
                    })
                    break  # יציאה מלולאת הצעדים
                
                if len(buffer) < MIN_BUFFER_SIZE_FOR_TRAINING:  # אם אין מספיק דוגמאות בחוצץ
                    continue  # המשך לאסוף עוד דוגמאות

                states, actions, rewards, next_states, dones = buffer.sample(batch_size)  # דגימה מה buffer
                Q_values = player.Q(states, actions)  # חישוב הקיו עבור המצבים הנוכחיים
                next_actions, Q_hat_Values = player_hat.get_Actions_Values(next_states)  # חישוב פעולות וקיו של ה target

                loss = player.model.loss(Q_values, rewards, Q_hat_Values, dones)  # השגיאה
                losses.append(loss.item())  # שמירת ערך השגיאה ברשימה
                wandb.log({"loss": loss.item(), "step": step})  # שמירת השגיאה ב wandb
                                
                loss.backward()  # מעבר לאחור לחישוב גרדיאנטים
                optim.step()  # עדכון פרמטרים באופטימייזר
                optim.zero_grad()  # איפוס גרדיאנטים לפני צעד הבא
                scheduler.step()  # עדכון שיעור הלמידה לפי מתזמן

                if epoch % C == 0:  # כל C אפוקים מעדכנים את מודל היעד
                    player_hat.model.load_state_dict(player.model.state_dict())  # העתקת הפרמטרים
                    
                step += 1  # הגדלת מונה הצעדים
            
            if epoch % 100 == 0 and epoch > 0:  # הדפסת סטטיסטיקה כל 100 אפוקים
                avg_score = sum(scores[-100:]) / 100  # ממוצע ציון אחרון 100
                avg_loss = sum(losses[-100:]) / len(losses[-100:]) if losses else 0  # ממוצע שגיאה
                avg_reward = sum(episode_rewards[-100:]) / 100  # ממוצע תגמול
                epsilon = player.get_epsilon(epoch)  # ערך אפסילון נוכחי
                print(f"\n=== Epoch {epoch}/{epochs} ===")
                print(f"Avg Score (last 100): {avg_score:.2f}")
                print(f"Avg Reward (last 100): {avg_reward:.2f}")
                print(f"Avg Loss (last 100): {avg_loss:.6f}")
                print(f"Epsilon: {epsilon:.4f}")
                print(f"Buffer Size: {len(buffer)}")
                print(f"Best Score: {max(scores) if scores else 0}")
                wandb.log({  # רישום ממוצעים ל wandb
                    "avg_score": avg_score,
                    "avg_reward": avg_reward,
                    "avg_loss": avg_loss,
                    "epsilon": epsilon,
                    "best_score": max(scores) if scores else 0,
                })
                torch.save(player.model.state_dict(), Model_Path)  # שמירת המודל
                torch.save(buffer, "Data/Buffer.pth")  # שמירת ה buffer
            
            
            
            env.reset()       
        try:
            wandb_run.finish()
        except Exception:
            pass

if __name__ == "__main__":
    game = Game()
    game.train()