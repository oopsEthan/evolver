import pygame
from utilities.config import TILE_SIZE, MAX_GRID_X, MAX_GRID_Y, GRID_DIAGONALS, GRID_CARDINALS, GRID_OCCUPANCY

def to_grid(vec2: pygame.Vector2) -> tuple[int, int]:
    """Converts a pixel-based Vector2 position to (x, y) grid coordinates"""
    return int(vec2.x // TILE_SIZE), int(vec2.y // TILE_SIZE)

def to_pixel(coords: tuple[int, int]) -> pygame.Vector2:
    """Converts grid (x, y) coordinates to a pixel-based Vector2 centered in the grid location"""
    x, y = coords
    return pygame.Vector2(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2)

def within_bounds(coords: tuple[int, int]) -> bool:
    """Checks if a coordinate is inside the bounds of the simulation"""
    x, y = coords
    return 0 <= x < MAX_GRID_X and 0 <= y < MAX_GRID_Y

def tile_occupied(coords: tuple[int, int]) -> bool:
    """Checks if a tile is occupied, returning True if so, False if it isn't"""
    occupants = GRID_OCCUPANCY.get(coords, [])
    return len(occupants) > 0

def relocate_object_on_GO(obj: object, new_coords: tuple[int, int]):
    """Updates the object's coords in GRID_OCCUPANCY"""
    remove_object_from_GO(obj)
    add_object_to_GO(obj, new_coords)
    return to_pixel(new_coords), new_coords

def remove_object_from_GO(obj: object):
    """Removes an object from GRID_OCCUPANCY"""
    coords = obj.grid_pos

    if coords in GRID_OCCUPANCY:
        if obj in GRID_OCCUPANCY[coords]:
            GRID_OCCUPANCY.get(coords).remove(obj)
            if not GRID_OCCUPANCY[coords]:
                del GRID_OCCUPANCY[coords]

def add_object_to_GO(obj: object, coords: tuple[int, int]):
    """Adds an object to GRID_OCCUPANCY"""
    if coords not in GRID_OCCUPANCY:
        GRID_OCCUPANCY[coords] = []

    GRID_OCCUPANCY[coords].append(obj)

def get_objects_at(coords: tuple[int, int]) -> object:
    """Checks the GRID_OCCUPANCY for an object and returns list"""
    return GRID_OCCUPANCY.get(coords, []) if tile_occupied(coords) else []

def get_available_adjacents(grid_coords: tuple[int, int], diagonals: bool=False, cardinals: bool=True):
        available_adjacent_tiles = []
        positions_to_check = []

        if diagonals:
            positions_to_check += GRID_DIAGONALS

        if cardinals:
            positions_to_check += GRID_CARDINALS
        
        for coord in positions_to_check:
            pos = (grid_coords[0] + coord[0], grid_coords[1] + coord[1])

            if not within_bounds(pos):
                continue
            if tile_occupied(pos):
                continue

            available_adjacent_tiles.append(pos)

        return available_adjacent_tiles

def is_surrounded(grid_coords: tuple[int, int]) -> bool:
    """If there are no available adjacent cardinal positions, return True"""
    return False if get_available_adjacents(grid_coords) else True