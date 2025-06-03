import pygame
from utilities.config import CELL_SIZE

def to_grid(vec2: pygame.Vector2) -> tuple[int, int]:
    """Converts a pixel-based Vector2 position to (x, y) grid coordinates"""
    return int(vec2.x // CELL_SIZE), int(vec2.y // CELL_SIZE)

def to_pixel(coords: tuple[int, int]) -> pygame.Vector2:
    """Converts grid (x, y) coordinates to a pixel-based Vector2 centered in the cell"""
    x, y = coords
    return pygame.Vector2(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2)