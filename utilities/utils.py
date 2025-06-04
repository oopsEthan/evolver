import pygame
from utilities.config import TILE_SIZE, ACTIVE_OBJECTS, MAX_GRID_X, MAX_GRID_Y, GRID_DIAGONALS, GRID_OCCUPANCY

def to_grid(vec2: pygame.Vector2) -> tuple[int, int]:
    """Converts a pixel-based Vector2 position to (x, y) grid coordinates"""
    return int(vec2.x // TILE_SIZE), int(vec2.y // TILE_SIZE)

def to_pixel(coords: tuple[int, int]) -> pygame.Vector2:
    """Converts grid (x, y) coordinates to a pixel-based Vector2 centered in the grid location"""
    x, y = coords
    return pygame.Vector2(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2)


## Collision handling

def tile_available(coords: tuple[int, int], ignore_tags: list[str]=None) -> bool:
    """Checks if a tile is empty/available, ignore_tags ignores objects by tag"""
    if not ignore_tags:
        ignore_tags = []

    occupants = GRID_OCCUPANCY.get(coords, [])
    return all(obj.tag in ignore_tags for obj in occupants)

def change_tile_occupancy(obj, new_coords: tuple[int, int]):
    """Updates the objects coords in the memory for searching"""
    current_coords = obj.get_grid()

    if obj in GRID_OCCUPANCY.get(current_coords, []):
        GRID_OCCUPANCY[current_coords].remove(obj)
        if not GRID_OCCUPANCY[current_coords]:
            del GRID_OCCUPANCY[current_coords]

    if new_coords not in GRID_OCCUPANCY:
        GRID_OCCUPANCY[new_coords] = []
    
    GRID_OCCUPANCY[new_coords].append(obj)

def within_bounds(coords: tuple) -> bool:
        """Check to see if the coords is within bounds, accepts grid coords"""
        x, y = coords
        return 0 <= x < MAX_GRID_X and 0 <= y < MAX_GRID_Y

# Path finding

def get_surrounding_tiles(grid_coords: tuple[int, int]) -> list:
    adjacents = []

    for coord in GRID_DIAGONALS + GRID_DIAGONALS:
        x = grid_coords[0] + coord[0]
        y = grid_coords[1] + coord[1]
        adjacents.append((x, y))
    
    return adjacents