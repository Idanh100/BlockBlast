import torch
from Environment2 import Environment  # ייבוא סביבת המשחק
from Model import DQN  # ייבוא הסוכן DQN
from Replay_Buffer import ReplayBuffer  # ייבוא מאגר החזרה
from Ai_Agent2 import Ai_Agent
import os
import wandb

def main ():
    # פונקציה ראשית לאימון הסוכן

    if torch.cuda.is_available():
        device = torch.device('cuda')  # שימוש ב-GPU אם זמין
    else:
        device = torch.device('cpu')  # אחרת CPU

    best_score = 0  # ציון הטוב ביותר

    ####### params and models ############  # פרמטרים ומודלים
    player = Ai_Agent # יצירת סוכן DQN
    player_hat = DQN()  # סוכן עזר ליעד
    player_hat.DQN = player.DQN.copy()  # העתקת המודל
    batch_size = 128  # גודל אצווה
    buffer = ReplayBuffer(path=None)  # מאגר חזרה
    learning_rate = 0.0001  # קצב למידה
    ephocs = 200000  # מספר אפוקים
    start_epoch = 0  # אפוק התחלתי
    C, tau = 3, 0.001  # פרמטרים לעדכון
    loss = torch.tensor(0)  # הפסד
    avg = 0  # ממוצע
    scores, losses, avg_score = [], [], []  # רשימות לציונים והפסדים
    optim = torch.optim.Adam(player.DQN.parameters(), lr=learning_rate)  # אופטימייזר
    # scheduler = torch.optim.lr_scheduler.StepLR(optim,100000, gamma=0.50)  # מתזמן קצב למידה (מבוטל)
    scheduler = torch.optim.lr_scheduler.MultiStepLR(optim,[5000*1000, 10000*1000, 15000*1000, 20000*1000, 25000*1000, 30000*1000], gamma=0.5)  # מתזמן מרובה שלבים
    step = 0  # צעד

    ######### checkpoint Load ############  # טעינת נקודת ביקורת
    num = 200
    checkpoint_path = f"Data/checkpoint{num}.pth"
    buffer_path = f"Data/buffer{num}.pth"
    resume_wandb = False
    if os.path.exists(checkpoint_path):
        resume_wandb = True
        checkpoint = torch.load(checkpoint_path)
        start_epoch = checkpoint['epoch']+1
        player.DQN.load_state_dict(checkpoint['model_state_dict'])
        player_hat.DQN.load_state_dict(checkpoint['model_state_dict'])
        optim.load_state_dict(checkpoint['optimizer_state_dict'])
        scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        buffer = torch.load(buffer_path)
        losses = checkpoint['loss']
        scores = checkpoint['scores']
        avg_score = checkpoint['avg_score']
    player.DQN.train()  # מצב אימון
    player_hat.DQN.eval()  # מצב הערכה
    
    ################# Wandb.init #####################  # אתחול Wandb לרישום
    
    wandb.init(
        # set the wandb project where this run will be logged
        project="Block_Blast",  # שינוי לפרויקט Block Blast
        resume=resume_wandb, 
        id=f'Block_Blast {num}',
        # track hyperparameters and run metadata
        config={
        "name": f"Block_Blast {num}",
        "checkpoint": checkpoint_path,
        "learning_rate": learning_rate,
        "Schedule": f'{str(scheduler.milestones)} gamma={str(scheduler.gamma)}',
        "epochs": ephocs,
        "start_epoch": start_epoch,
        "gamma": 0.99,
        "batch_size": batch_size, 
        "C": C,
        "tau":tau,
        "Model":str(player.DQN),
        "device": str(device)
        }
    )
    # wandb.config.update({"Model":str(player.DQN)}, allow_val_change=True)
    
    #################################

    env = Environment()  # יצירת סביבת המשחק ללא תפאורה

    MIN_BUFFER = 1000  # גודל מינימלי למאגר לפני אימון

    for epoch in range(start_epoch, ephocs):  # לולאה על האפוקים
        env.restart()  # אתחול הסביבה
        end_of_game = False
        state = env.state()  # קבלת מצב נוכחי
        while not end_of_game:  # לולאה על המשחק
            print (step, end='\r')
            step += 1
            
            ############## Sample Environement #########################  # דגימה מהסביבה
            action = player.get_Action(state=state, epoch=epoch)  # קבלת פעולה מהסוכן
            reward, done = env.move(action=action)  # ביצוע פעולה וקבלת תגמול
            next_state = env.state()  # מצב הבא
            buffer.push(state, torch.tensor(action, dtype=torch.int64), torch.tensor(reward, dtype=torch.float32), 
                        next_state, torch.tensor(done, dtype=torch.float32))  # הוספה למאגר
            if done:
                best_score = max(best_score, env.score)  # עדכון ציון טוב ביותר
                break

            state = next_state  # עדכון מצב
            
            if len(buffer) < MIN_BUFFER:  # אם המאגר קטן מדי, דלג
                continue
    
            ############## Train ################  # אימון
            states, actions, rewards, next_states, dones = buffer.sample(batch_size)  # דגימה מאגר
            Q_values = player.Q(states, actions)  # ערכי Q
            next_actions, Q_hat_Values = player_hat.get_Actions_Values(next_states)  # ערכי Q ליעד

            loss = player.DQN.loss(Q_values, rewards, Q_hat_Values, dones)  # חישוב הפסד
            loss.backward()  # backpropagation
            optim.step()  # עדכון משקלים
            optim.zero_grad()  # איפוס גרדיאנטים
            scheduler.step()  # עדכון מתזמן

        if epoch % C == 0:  # עדכון מודל יעד כל C אפוקים
            # player_hat.DQN.load_state_dict(player.DQN.state_dict())
            player_hat.fix_update(dqn=player.DQN)
            # player_hat.soft_update(dqn=player.DQN, tau=tau)

        #########################################
        print (f'epoch: {epoch} loss: {loss:.7f} LR: {scheduler.get_last_lr()} step: {step} ' \
               f'score: {env.score} level: {env.level} best_score: {best_score}')  # הדפסת סטטיסטיקות
        step = 0
        if epoch % 10 == 0:
            scores.append(env.score)
            losses.append(loss.item())

        avg = (avg * (epoch % 10) + env.score) / (epoch % 10 + 1)  # חישוב ממוצע
        if (epoch + 1) % 10 == 0:
            avg_score.append(avg)
            wandb.log ({  # רישום ל-Wandb
                "score": env.score,
                "loss": loss.item(),
                "avg_score": avg
            })
            print (f'average score last 10 games: {avg} ')
            avg = 0

        if epoch % 1000 == 0 and epoch > 0:  # שמירת נקודת ביקורת כל 1000 אפוקים
            checkpoint = {
                'epoch': epoch,
                'model_state_dict': player.DQN.state_dict(),
                'optimizer_state_dict': optim.state_dict(),
                'scheduler_state_dict': scheduler.state_dict(),
                'loss': losses,
                'scores':scores,
                'avg_score': avg_score
            }
            torch.save(checkpoint, checkpoint_path)
            torch.save(buffer, buffer_path)


if __name__ == "__main__":
    main ()