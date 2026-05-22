# ==================== GRAPHICS & DISPLAY ====================
# FPS and screen settings
FPS = 60

# Grid configuration (relative to screen size)
# GRID_SIZE is calculated as width / 30
# GRID_ORIGIN_X is calculated as (width / 2) - (GRID_SIZE * 4)
# GRID_ORIGIN_Y is calculated as height / 10
GRID_MARGIN = 4

# Color definitions (RGB tuples)
COLOR_RED = (220, 70, 70)
COLOR_YELLOW = (240, 200, 50)
COLOR_ORANGE = (240, 130, 50)
COLOR_GREEN = (100, 200, 100)
COLOR_BLUE = (100, 100, 240)
COLOR_PURPLE = (180, 100, 240)

COLOR_WHITE = (255, 255, 255)
COLOR_DARK_BLUE = (35, 50, 95)  # Background
COLOR_DARKER_BLUE = (25, 35, 70)  # Grid background
COLOR_LIGHT_BLUE = (80, 100, 170)  # Accent
COLOR_HIGHLIGHT = (100, 150, 255)
COLOR_INVALID_HIGHLIGHT = (150, 50, 50, 128)
COLOR_COMPLETE_LINE_HIGHLIGHT = (120, 240, 120, 160)
COLOR_GOLD = (255, 215, 0)

# List of block colors (used in cycling through colors)
BLOCK_COLORS = [
    COLOR_RED,
    COLOR_YELLOW,
    COLOR_ORANGE,
    COLOR_GREEN,
    COLOR_BLUE,
    COLOR_PURPLE
]

# ==================== GAME MECHANICS ====================
# Board dimensions
BOARD_WIDTH = 8
BOARD_HEIGHT = 8

# Number of blocks shown at a time
NUM_BLOCKS_PER_TURN = 3

# Game timing (milliseconds)
AI_MOVE_DELAY = 750  # Delay between AI moves for visualization
HUMAN_MOVE_DELAY = 0  # Delay for human player moves

# ==================== REWARDS ====================
# Reward values for different game actions
REWARD_EXPLODE = 10  # Reward for completing a line/block
REWARD_SQUARES_PER_BLOCK = 2  # Reward per square removed
REWARD_SQUARES_IN_SAME_ROW_OR_COL = 1  # Reward for squares in affected rows/cols

# ==================== AI AGENT SETTINGS ====================
# Epsilon greedy exploration parameters
EPSILON_START = 1.0  # Initial exploration rate
EPSILON_END = 0.01  # Minimum exploration rate
EPSILON_DECAY = 500  # Number of epochs for epsilon decay

# ==================== TRAINING HYPERPARAMETERS ====================
# Learning and optimization
LEARNING_RATE = 0.00001
BATCH_SIZE = 50
GAMMA = 0.99  # Discount factor for future rewards

# Training configuration
NUM_EPOCHS = 20000
REPLAY_BUFFER_CAPACITY = 100000
MIN_BUFFER_SIZE_FOR_TRAINING = 5000  # Start training after this many experiences

# Model update frequency
NETWORK_UPDATE_FREQUENCY = 3  # Update target network every C steps

# Learning rate scheduler milestones
LR_SCHEDULER_MILESTONES = [5000, 10000, 15000]  # Epochs to reduce learning rate
LR_SCHEDULER_GAMMA = 0.5  # Multiply learning rate by this value

# ==================== FILE PATHS ====================
# Data and model directories
DATA_DIRECTORY = "Data/"
MODEL_PATH_TEMPLATE = f"{DATA_DIRECTORY}Model{{}}.ptn"  # Use with .format(model_number)
BUFFER_PATH_TEMPLATE = f"{DATA_DIRECTORY}Train{{}}.ptn"  # Use with .format(model_number)
DEFAULT_MODEL_NUMBER = 21

# ==================== WANDB SETTINGS ====================
# Weights & Biases logging configuration
WANDB_PROJECT = "Block_Blast"
WANDB_ENTITY = None  # Set if you want to log to a specific entity

# ==================== GAME BOARD SHAPES ====================
# Available block shapes for the game
BLOCK_SHAPES = {
    "square": [[1, 1], [1, 1]],
    "line2": [[1, 1]],
    "line3": [[1, 1, 1]],
    "line4": [[1, 1, 1, 1]],
    "line5": [[1, 1, 1, 1, 1]],
    "col2": [[1], [1]],
    "col3": [[1], [1], [1]],
    "col4": [[1], [1], [1], [1]],
    "col5": [[1], [1], [1], [1], [1]],
    "T": [[0, 1, 0], [1, 1, 1]],
    "T_inverted": [[1, 1, 1], [0, 1, 0]],
    "T_right": [[1, 0], [1, 1], [1, 0]],
    "T_left": [[0, 1], [1, 1], [0, 1]],
    "L": [[1, 0], [1, 0], [1, 1]],
    "L_flipped": [[0, 1], [0, 1], [1, 1]],
    "L_rotated": [[1, 1, 1], [1, 0, 0]],
    "L_rotated_flipped": [[1, 1, 1], [0, 0, 1]],
    "Z": [[1, 1, 0], [0, 1, 1]],
    "Z_vertical": [[0, 1], [1, 1], [1, 0]],
    "S": [[0, 1, 1], [1, 1, 0]],
    "S_vertical": [[1, 0], [1, 1], [0, 1]],
    "plus": [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
    "dot1": [[1]],
    "dot2": [[1]],
    "dot3": [[1]],
    "dot4": [[1]],
    "dot6": [[1]],
    "dot7": [[1]],
    "dot8": [[1]],
    "dot9": [[1]],
    "dot10": [[1]],
    "dot11": [[1]],
    "dot12": [[1]],
    "dot13": [[1]],
    "dot14": [[1]],
    "dot15": [[1]],
    "small_square": [[1, 1], [1, 1]],
    "corner": [[1, 1], [1, 0]],
    "corner_flipped": [[1, 1], [0, 1]],
    "corner_rotated": [[0, 1], [1, 1]],
    "corner_rotated_flipped": [[1, 0], [1, 1]],
    "U": [[1, 0, 1], [1, 1, 1]],
    "U_rotated": [[1, 1], [1, 0], [1, 1]],
    "U_inverted": [[1, 1, 1], [1, 0, 1]],
    "U_rotated_flipped": [[1, 1], [0, 1], [1, 1]],
    "2x3": [[1, 1, 1], [1, 1, 1]],
    "3x3": [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
}
