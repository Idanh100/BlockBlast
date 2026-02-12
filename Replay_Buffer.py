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
            self.buffer = deque(maxlen=capacity)

    def push (self, state, action, reward, next_state, done):
        '''
        state, action, next_state = tensors
        reward, done = tensors
        '''
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample (self, batch_size):
        if (batch_size > self.__len__()):
            batch_size = self.__len__()
        state_tensors, action_tensors, reward_tensors, next_state_tensors, dones_tensor = zip(*random.sample(self.buffer, batch_size))
        states = torch.cat(state_tensors, dim=0)  # states are [1, 8, 8] each, cat along dim 0 -> [batch, 8, 8]
        states = states.unsqueeze(1)  # add channel dimension -> [batch, 1, 8, 8]
        actions = torch.vstack(action_tensors)
        rewards = torch.vstack(reward_tensors)
        next_states = torch.cat(next_state_tensors, dim=0)
        next_states = next_states.unsqueeze(1)  # add channel dimension -> [batch, 1, 8, 8]
        dones = torch.vstack(dones_tensor)
        return states, actions, rewards, next_states, dones

    def __len__(self):
        return len(self.buffer)
