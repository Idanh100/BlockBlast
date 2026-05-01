import pygame
import torch
import torch.nn as nn
import torch.nn.functional as F
from State2 import State
from Environment2 import Environment
from CONSTANTS import *

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
        self.State_Tensor = self.Current_State.TensorState(self.Current_State.Board)
        self.All_Moves = self.env.GetAllPossibleMoves(self.Current_State)
        self.All_After_States = self.env.AfterState(self.Current_State, self.All_Moves)
        
        
    def forward(self, All_After_States):
        All_After_States = self.pool(F.relu(self.conv1(All_After_States)))
        All_After_States = self.pool(F.relu(self.conv2(All_After_States)))
        All_After_States = All_After_States.view(-1, 32 * 2 * 2)
        All_After_States = F.relu(self.fc1(All_After_States))
        All_After_States = F.relu(self.fc2(All_After_States))
        All_After_States = self.fc3(All_After_States)
        return All_After_States
    
    def loss(self, Q_values, rewards, Q_hat_values, dones, gamma=GAMMA):
        target_q_values = rewards + gamma * Q_hat_values * (1 - dones)
        
        mse_loss = F.mse_loss(Q_values, target_q_values)
        return mse_loss
    
    def loadModel (self, file):
        self.model = torch.load(file)
    
    def save_param (self, path):
        self.DQN.save_params(path)