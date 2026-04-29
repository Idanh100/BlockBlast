import pygame
import torch
import copy
import random
from State2 import State
from Environment2 import Environment
from Model import DQN
from Block import Block
from CONSTANTS import *

class Ai_Agent:
    def __init__(self, model=None, train=True):
        """Initialize AI Agent.
        
        Args:
            model: DQN model instance for choosing actions. If None, creates a new one.
        """
        # pygame.init()
        info = pygame.display.get_desktop_sizes()[0]
        self.width, self.height = info

        self.GRID_ORIGIN_Y = self.height / 10
        self.GRID_SIZE = self.width / 30
        self.GRID_ORIGIN_X = (self.width / 2) - (self.GRID_SIZE * 4)
        self.GRID_MARGIN = GRID_MARGIN

        self.model = model if model else DQN()
        self.selected_block = None
        self.env = Environment(State())
        self.train = train
        
    def Q (self, states, actions):
        Q_values = self.model(states)
        return Q_values

    def get_Actions_Values(self, next_states):
        with torch.no_grad():
            q_values = self.model(next_states)
        best_actions = torch.argmax(q_values, dim=1, keepdim=True)
        return best_actions, q_values


    def get_action (self, state, events=None, epoch=0):
        action, _ = self.get_action_train(state, epoch)
        return action

    def get_action_train(self, state, epoch=0):
        moves = self.get_all_moves(state)
        after_state_tensors = self.get_after_states(moves, state)
                
        if self.train and random.random() < self.get_epsilon(epoch):
            best_idx = random.randint(0, len(moves) - 1)
            best_move = moves[best_idx]
            return self.move_to_action(best_move),  after_state_tensors[best_idx] 

        

        with torch.no_grad():
            q_values = self.model(after_state_tensors)

        best_idx = torch.argmax(q_values)
        best_move = moves[best_idx]
        best_after_state_tensor = after_state_tensors[best_idx] 
        action = self.move_to_action(best_move)
        test = action, best_after_state_tensor
        return action, best_after_state_tensor
      
        
    
    def get_all_moves (self, state):
        moves = []
        for block in state.Blocks:
            shape_h = len(block.shape)
            shape_w = len(block.shape[0]) if shape_h > 0 else 0
            
            max_y = state.Board.shape[0] - shape_h
            max_x = state.Board.shape[1] - shape_w
            if max_y < 0 or max_x < 0:
                continue

            for y in range(0, max_y + 1):
                for x in range(0, max_x + 1):
                    if self.env.is_valid_move(state, block, (x, y)):
                        moves.append((block, (x, y)))
        return moves

    def get_after_states (self, moves, state):
        after_states = []
        for move in moves:
                block, pos = move
                grid_x, grid_y = pos
                
                new_state = copy.deepcopy(state)
                self.env.fix_block_to_board(new_state, block, pos)
                self.env.check_and_explode_rows(new_state)
                
                if not new_state.Blocks:
                    self.env.set_random_block(new_state)
                
                state_tensor = new_state.TensorState(new_state.Board)
                state_tensor = state_tensor.view(1, 8, 8)
                after_states.append(state_tensor)
        
        after_tensors = torch.stack(after_states, dim=0)
        return after_tensors
    
    def move_to_action (self, best_move):
        block, (grid_x, grid_y) = best_move
            

        pixel_x = self.GRID_ORIGIN_X + grid_x * self.GRID_SIZE
        pixel_y = self.GRID_ORIGIN_Y + grid_y * self.GRID_SIZE
        
        self.selected_block = block
        
        return (block, (pixel_x, pixel_y))
    
    def get_epsilon (self, epoch = 0, start=EPSILON_START, end=EPSILON_END, decay = EPSILON_DECAY):
        if epoch > decay:
            return end
        return start - (end - start) * (epoch / decay)
        
    def load_model(self, file):
        self.model.load_state_dict(torch.load(file))