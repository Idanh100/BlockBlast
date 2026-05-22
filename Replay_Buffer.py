from collections import deque
import random
import torch
import numpy as np

capacity = 100000

class ReplayBuffer:
    def __init__(self, capacity= capacity, path = None) -> None:
        if path:
            self.buffer = torch.load(path).buffer
        else:
            # יוצר deque מעגלי עם אורך מקסימלי
            self.buffer = deque(maxlen=capacity)

    # שמירת דוגמה חדשה ל buffer
    def push (self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))
    
    # דגימה אקראית של באצ' מתוך ה buffer
    def sample (self, batch_size):
        if (batch_size > self.__len__()):
            batch_size = self.__len__()
        state_tensors, action_tensors, reward_tensors, next_state_tensors, dones_tensor = zip(*random.sample(self.buffer, batch_size))
        # מחבר את כל המצבים לטנסור אחד
        states = torch.cat(state_tensors, dim=0)
        # מוסיף עוד תא לטנסור כדי שיתאים לרשת CNN
        states = states.unsqueeze(1) 
        # מחבר את כל הפעולות לטנסור אחד
        actions = torch.vstack(action_tensors)
        # מחבר את כל התגמולים לטנסור אחד
        rewards = torch.vstack(reward_tensors)
        # מחבר את כל המצבים הבאים לטנסור אחד
        next_states = torch.cat(next_state_tensors, dim=0)
        # מוסיף עוד תא לטנסור כדי שיתאים לרשת CNN
        next_states = next_states.unsqueeze(1)
        # מחבר את כל הערכים שאומרים אם המשחק נגמר
        dones = torch.vstack(dones_tensor)
        # מחזיר את הנתונים שישמשו לאימון
        return states, actions, rewards, next_states, dones

    # אורך הBuffer
    def __len__(self):
        return len(self.buffer)
