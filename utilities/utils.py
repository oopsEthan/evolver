import pygame
from config import CELL_SIZE

# Converts a pixel-based Vector2 position to (x, y) grid coordinates
def to_grid(vec2):
    return int(vec2.x // CELL_SIZE), int(vec2.y // CELL_SIZE)

# Converts grid (x, y) coordinates to a pixel-based Vector2 centered in the cell
def to_pixel(x, y):
    return pygame.Vector2(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2)