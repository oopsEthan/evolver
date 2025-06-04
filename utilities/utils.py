import pygame
from utilities.config import TILE_SIZE, ACTIVE_OBJECTS, MAX_GRID_X, MAX_GRID_Y, GRID_DIAGONALS, GRID_CARDINALS, GRID_OCCUPANCY

def to_grid(vec2: pygame.Vector2) -> tuple[int, int]:
    """Converts a pixel-based Vector2 position to (x, y) grid coordinates"""
    return int(vec2.x // TILE_SIZE), int(vec2.y // TILE_SIZE)

def to_pixel(coords: tuple[int, int]) -> pygame.Vector2:
    """Converts grid (x, y) coordinates to a pixel-based Vector2 centered in the grid location"""
    x, y = coords
    return pygame.Vector2(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2)


## Collision handling

def within_bounds(coords: tuple[int, int]):
    x, y = coords
    return 0 <= x < MAX_GRID_X and 0 <= y < MAX_GRID_Y

def tile_occupied(coords: tuple[int, int]) -> bool:
    """Checks if a tile is occupied, returning False if so, True if it is"""
    occupants = GRID_OCCUPANCY.get(coords, [])
    return len(occupants) > 0

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

# Path finding

def get_adjacent_tiles(grid_coords: tuple[int, int],
                       diagonals: bool=True,
                       cardinals: bool=True,
                       avoid_occupied: bool=False) -> list:
    """
    Returns a list of adjacent (x, y) tile coordinates around a given grid position.

    Parameters:
    - grid_coords: The (x, y) grid position to check around.
    - diagonals: If True, includes diagonal neighbors.
    - cardinals: If True, includes cardinal neighbors.
    - avoid_occupied: If True, excludes tiles that are currently occupied.

    Returns:
    - List of (x, y) tuples representing adjacent tiles.
    """

    adjacents = []
    positions_to_check = []

    if diagonals:
        positions_to_check += GRID_DIAGONALS

    if cardinals:
        positions_to_check += GRID_CARDINALS
    
    for coord in positions_to_check:
        pos = (grid_coords[0] + coord[0], grid_coords[1] + coord[1])

        if not within_bounds(pos):
            continue
        if avoid_occupied and tile_occupied(pos):
            continue

        adjacents.append(pos)
    
    return adjacents