from .constants import BOARD_WIDTH, BOARD_HEIGHT

def is_valid_position(y, x):
    return y >= 0 and x >= 0 and y < BOARD_HEIGHT and x < BOARD_WIDTH