import random

class Block:
    def __init__(self, shape, rect, color_id):
        self.shape = shape
        self.rect = rect
        self.color_id = color_id  # מזהה ייחודי לבלוק (מספר שמייצג צבע)
        
        RED = (220, 70, 70)
        YELLOW = (240, 200, 50)
        ORANGE = (240, 130, 50)
        GREEN = (100, 200, 100)
        BLUE = (100, 100, 240)
        PURPLE = (180, 100, 240)
        colors = [RED, YELLOW, ORANGE, GREEN, BLUE, PURPLE]
        
        self.color = colors[color_id % len(colors)]  # צבע הבלוק