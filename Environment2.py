import pygame
import random
import copy
import numpy as np
from types import SimpleNamespace
from Block import Block
from State2 import State
from Graphics2 import Graphics
import torch
from CONSTANTS import *

class Environment:
    
    REWARD_EXPLODE = REWARD_EXPLODE
    REWARD_SQUARES_PER_BLOCK = REWARD_SQUARES_PER_BLOCK
    REWARD_SQUARES_IN_SAME_ROW_OR_COL = REWARD_SQUARES_IN_SAME_ROW_OR_COL
    
    def __init__(self, state):

        self.state = state

        
        pygame.init()
        info = pygame.display.get_desktop_sizes()[0]
        self.width, self.height = info

        self.GRID_ORIGIN_Y = self.height / 10
        self.GRID_SIZE = self.width / 30
        self.GRID_ORIGIN_X = (self.width / 2) - (self.GRID_SIZE * 4)
        self.GRID_MARGIN = GRID_MARGIN
        self.num_explosions = 0
        self.last_preplacement_sum = 0
        self.last_move_valid = False

    def all_shapes(self):
        return BLOCK_SHAPES
    
    def reset(self):
        self.state = State()
        self.set_random_block()

    def shutdown(self):
        pygame.quit()

    def set_random_block(self, state: State = None):
        if state is None:
            state = self.state
        all_shapes = self.all_shapes()
        blocks = random.sample(list(all_shapes.values()), 3)
        blocks_lst = []
        
        start_x = (self.width / 2) - (self.width / 4)
        start_y = self.height / 1.5
        spacing = self.width / 5

        for i, block in enumerate(blocks):
            rect = pygame.Rect(start_x + i * spacing, start_y, 50, 50)
            new_block = Block(block, rect, i + 1)
            new_block.initial_position = rect.copy()
            blocks_lst.append(new_block)

        state.Blocks = set(blocks_lst)

    def move(self, state: State, action: tuple):
        block, position = action

        grid_x = int((position[0] - self.GRID_ORIGIN_X) / self.GRID_SIZE)
        grid_y = int((position[1] - self.GRID_ORIGIN_Y) / self.GRID_SIZE)

        filled_count = 0
        if self.is_valid_move(state, block, (grid_x, grid_y)):
            filled_count = self.sum_ones_in_affected_rows_cols(state, block, (grid_x, grid_y))
            self.fix_block_to_board(state, block, (grid_x, grid_y))
            self.print_block_squares(block.shape)

            num_expl = self.check_and_explode_rows(state)
            self.num_explosions = num_expl
            self.last_move_valid = True
        else:
            block.rect = block.initial_position.copy()
            self.last_move_valid = False
            self.num_explosions = 0

        self.check_and_generate_blocks()
        return filled_count
    
    def move_legal(self, state: State, action: tuple):
        block, position = action

        grid_x = int((position[0] - self.GRID_ORIGIN_X) / self.GRID_SIZE)
        grid_y = int((position[1] - self.GRID_ORIGIN_Y) / self.GRID_SIZE)
        filled_count = self.sum_ones_in_affected_rows_cols(state, block, (grid_x, grid_y))
        self.fix_block_to_board(state, block, (grid_x, grid_y))
        self.check_and_explode_rows(state)
        self.check_and_generate_blocks()
        reward = self.reward()
        return reward

    def Get_Reward_Args(self, state: State, action: tuple):
        if not self.last_move_valid:
            return 0
        
        block, position = action

        grid_x = int((position[0] - self.GRID_ORIGIN_X) / self.GRID_SIZE)
        grid_y = int((position[1] - self.GRID_ORIGIN_Y) / self.GRID_SIZE)

        reward = self.Get_Reward(state, block, grid_x, grid_y)
        return reward

    def Get_Reward(self, state, block, grid_x, grid_y):
        reward = self.count_squares_of_block(block.shape) * self.REWARD_SQUARES_PER_BLOCK
        reward += self.sum_ones_in_affected_rows_cols(state, block, (grid_x, grid_y)) * self.REWARD_SQUARES_IN_SAME_ROW_OR_COL
        reward += self.num_explosions * self.REWARD_EXPLODE
        return reward

    def count_squares_of_block(self, shape):
        return sum(sum(row) for row in shape)

    def print_block_squares(self, shape):
        count = self.count_squares_of_block(shape)

    def count_ones_per_row_col(self, state: State):
        board = state.Board
        board_arr = np.array(board)
        row_counts = np.sum(board_arr != 0, axis=1).tolist()
        col_counts = np.sum(board_arr != 0, axis=0).tolist()
        return row_counts, col_counts

    def sum_ones_in_affected_rows_cols(self, state: State, block: Block, position: tuple) -> int:
        shape_arr = np.array(getattr(block, 'shape', []))

        h, w = shape_arr.shape
        grid_x, grid_y = position

        board = np.array(state.Board)
        min_y = max(0, grid_y)
        min_x = max(0, grid_x)
        max_y = min(board.shape[0], grid_y + h)
        max_x = min(board.shape[1], grid_x + w)

        if min_y >= max_y or min_x >= max_x:
            return 0

        row_counts, col_counts = self.count_ones_per_row_col(state)

        total_rows = sum(row_counts[r] for r in range(min_y, max_y) if 0 <= r < len(row_counts))
        total_cols = sum(col_counts[c] for c in range(min_x, max_x) if 0 <= c < len(col_counts))

        total = int(total_rows + total_cols) - self.count_squares_of_block(block.shape) * 2
        return total

    def is_valid_move(self, state: State, block: Block, position: tuple) -> bool:
        board = state.Board
        grid_x, grid_y = position

        shape = getattr(block, 'shape', None)
        if shape is None:
            return False

        shape_arr = np.array(shape)
        h, w = shape_arr.shape

        if grid_x < 0 or grid_y < 0 or (grid_x + w) > board.shape[1] or (grid_y + h) > board.shape[0]:
            return False

        board_slice = board[grid_y:grid_y + h, grid_x:grid_x + w]
        if np.any(board_slice * shape_arr != 0):
            return False

        return True

    def fix_block_to_board(self, state: State, block: Block, position: tuple):
        board = state.Board
        grid_x, grid_y = position
        placed_cells = 0

        for y, row in enumerate(block.shape):
            for x, cell in enumerate(row):
                if cell == 1:
                    board_x = grid_x + x
                    board_y = grid_y + y
                    if 0 <= board_x < len(board[0]) and 0 <= board_y < len(board):
                        board[board_y][board_x] = block.color_id
                        placed_cells += 1

        state.score += placed_cells

        if block in state.Blocks:
            state.Blocks.remove(block)

    def check_and_generate_blocks(self):
        if not self.state.Blocks:
            self.set_random_block()

    def check_and_explode_rows(self, state: State):
        board = state.Board
        rows_to_explode = [y for y in range(board.shape[0]) if all(board[y, :] != 0)]
        cols_to_explode = [x for x in range(board.shape[1]) if all(board[:, x] != 0)]

        for row in rows_to_explode:
            board[row, :] = 0

        for col in cols_to_explode:
            board[:, col] = 0

        num_explosions = len(rows_to_explode) + len(cols_to_explode)
        if num_explosions > 0:
            state.turns_since_last_explosion = 0
            if state.in_combo:
                state.combo_count += num_explosions
            else:
                state.combo_count = num_explosions

            for i in range(num_explosions):
                state.score += (state.combo_count + i) * 10

            state.in_combo = True
        else:
            state.turns_since_last_explosion += 1
            if state.turns_since_last_explosion > 2:
                state.in_combo = False
                state.combo_count = 0
        return num_explosions

    def is_game_over(self, state: State) -> bool:
        board = state.Board
        for block in state.Blocks:
            for y in range(len(board)):
                for x in range(len(board[0])):
                    if self.is_valid_move(state, block, (x, y)):
                        return False
        print("Game Over! Score:", state.score)
        return True

    def GetAllPossibleMoves(self, state: State):
        board = state.Board
        shapes = self.all_shapes()
        legal_moves = []

        for name, shape in shapes.items():
            shape_h = len(shape)
            shape_w = len(shape[0]) if shape_h > 0 else 0

            max_y = board.shape[0] - shape_h
            max_x = board.shape[1] - shape_w
            if max_y < 0 or max_x < 0:
                continue

            for y in range(0, max_y + 1):
                for x in range(0, max_x + 1):
                    dummy = SimpleNamespace(shape=shape)
                    if self.is_valid_move(state, dummy, (x, y)):
                        legal_moves.append((name, shape, (x, y)))

        return tuple(legal_moves)

    def AfterState(self, state: State, moves):
        resulting_states = []
        for mv in moves:
            try:
                name, shape, pos = mv
            except Exception:
                continue
            x, y = pos

            new_state = copy.deepcopy(state)

            dummy_block = Block(shape, pygame.Rect(0, 0, 0, 0), 1)

            self.fix_block_to_board(new_state, dummy_block, (x, y))

            self.check_and_explode_rows(new_state)

            if not new_state.Blocks:
                self.set_random_block(new_state)

            resulting_states.append(new_state)

        return resulting_states
    
    def tensor_shape(self, shape):
        shape_T = torch.tensor(shape, dtype=torch.float32)
        return shape_T
    
    def GetAllAfterStates(self, state):
        all_moves = self.GetAllPossibleMoves(state)
        all_after_states = self.AfterState(state, all_moves)
        return tuple(all_after_states)
        