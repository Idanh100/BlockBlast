import pygame
import torch
import torch.nn as nn
import torch.nn.functional as F
from State2 import State
from Environment2 import Environment

class DQN(nn.Module):
    def __init__(self):
        super(DQN, self).__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)  # input: (1, 8, 8) -> output: (16, 8, 8)
        self.pool = nn.MaxPool2d(2, 2)  # output: (16, 4, 4)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)  # output: (32, 4, 4)
        self.fc1 = nn.Linear(32 * 2 * 2, 128)  # 128 -> 128
        self.fc2 = nn.Linear(128, 64)  # 128 -> 64
        self.fc3 = nn.Linear(64, 1)  # 64 -> 1 (Q-value output)

        self.env = Environment(State())
        self.Current_State = State()
        self.State_Tensor = self.Current_State.TensorState(self.Current_State.Board)  # יוצר tensor של הלוח בstate
        self.All_Moves = self.env.GetAllPossibleMoves(self.Current_State)  # מקבל את כל המהלכים החוקיים בלוח
        self.All_After_States = self.env.AfterState(self.Current_State, self.All_Moves)  # מקבל את כל המצבים האפשריים לאחר כל המהלכים
        
        
    def forward(self, All_After_States):
        All_After_States = self.pool(F.relu(self.conv1(All_After_States)))
        All_After_States = self.pool(F.relu(self.conv2(All_After_States)))
        All_After_States = All_After_States.view(-1, 32 * 2 * 2)
        All_After_States = F.relu(self.fc1(All_After_States))
        All_After_States = F.relu(self.fc2(All_After_States))
        All_After_States = self.fc3(All_After_States)
        return All_After_States
    
    def loss(self, Q_values, rewards, Q_hat_values, dones, gamma=0.99):
        """DQN Loss function
        
        Args:
            Q_values: Q(s,a) from current network - shape [batch, 1]
            rewards: immediate rewards - shape [batch, 1]
            Q_hat_values: max Q(s', a') from target network - shape [batch, 1]
            dones: terminal state mask - shape [batch, 1]
            gamma: discount factor
        
        Returns:
            mse_loss: mean squared error between Q and target
        """
        # Target Q-value: r + γ * max Q_hat(s', a') * (1 - done)
        # Multiply by (1-done) to zero out Q_hat when episode is done
        target_q_values = rewards + gamma * Q_hat_values * (1 - dones)
        
        # DQN loss
        mse_loss = F.mse_loss(Q_values, target_q_values)
        return mse_loss
    
    def loadModel (self, file):
        self.model = torch.load(file)
    
    def save_param (self, path):
        self.DQN.save_params(path)

    def load_params (self, path):
        self.DQN.load_params(path)