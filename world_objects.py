import pygame
from random import randrange, shuffle
from utilities.config import *
from utilities.utils import *

# God of all objects, they are made in His image
class Simulation_Object:
    def __init__(self):
        self.move_to()
        self.energy_value = 0

    def move_to(self, loc: tuple=None) -> None:
        """Moves a simulation object to loc (x,y) on the grid, if no loc provided, random"""
        if not loc:
            while True:
                loc = randrange(0, MAX_GRID_X), randrange(0, MAX_GRID_Y)
                if not tile_occupied(loc):
                    break
        
        self.current_loc = to_pixel(loc)
        change_tile_occupancy(self, loc)

    def get_grid(self) -> tuple:
        """Returns the grid coordinates (x,y) of the object"""
        return to_grid(self.current_loc)
    
    def get_grid_distance_to(self, target: 'Simulation_Object') -> int:
        """Gets the grid distance between object and the target"""
        gx, gy = self.get_grid()
        tx, ty = target.get_grid()
        return abs(gx - tx) + abs(gy - ty)

    def is_adjacent_to(self, target: 'Simulation_Object') -> bool:
        """Checks if the target is adjacent to the object"""
        tx, ty = target.get_grid()
        dx, dy = self.get_grid()
        return abs(tx - dx) + abs(ty - dy) == 1

    # Indicate what happens when a dob interacts with the object, by default it returns an energy value
    def interact_with(self):
        return self.energy_value

    def register(self, object_class: object, object_tag: str, db: list) -> None:
        """Registers the object to the simulation"""
        self.id = object_class._id
        object_class._id += 1

        self.tag = object_tag
        self.db = db
        db.append(self)

# Food is food that you eat food eat food
class Food(Simulation_Object):
    _id = 0

    def __init__(self):
        super().__init__()
        self.register(Food, FOOD, ACTIVE_FOOD)
        
        self.eaten = False
        self.regrow_cooldown = FOOD_REGROWTH_COOLDOWN
        self.energy_value = FOOD_VALUE

    def exist(self, surface):
        if not self.eaten:
            pygame.draw.circle(surface, "red", self.current_loc, TILE_SIZE/2)

        # Food regrows, every tick counts the cooldown down 1
        else:
            if self.regrow_cooldown == 0:
                self.eaten = False
                self.regrow_cooldown = FOOD_REGROWTH_COOLDOWN
            
            self.regrow_cooldown -= 1

    # Food has to mark itself as eaten :(
    def interact_with(self):
        self.eaten = True
        return super().interact_with()

# Worter
class Water(Simulation_Object):
    _id = 0

    def __init__(self, starting_coords, chance_to_cascade=1):
        super().__init__()
        self.register(Water, WATER, ACTIVE_WATER)
        self.move_to(starting_coords)

        self.energy_value = WATER_VALUE
        
        self.cascade(chance_to_cascade)

    # Water is a Rect so it requires it's pixel-position to be adjusted by half a grid
    def exist(self, surface):
        offset_position = self.current_loc - pygame.Vector2(TILE_SIZE // 2, TILE_SIZE // 2)
        position = pygame.Rect(offset_position, GRID_UNIT)
        pygame.draw.rect(surface, "#47CBED", position)
    
    # Water attempts to cascade to simulate ponds, rivers, etc.
    # If water cascades, the water it spawns will also attempt to cascade
    def cascade(self, chance):
        if chance <= 0:
            return

        directions = GRID_CARDINALS.copy()
        shuffle(directions)

        for dx, dy in directions:
            grid_x, grid_y = self.get_grid()
            new_coords = (grid_x + dx, grid_y + dy)

            if tile_occupied(new_coords) and within_bounds(new_coords):
                continue

            if not tile_occupied(new_coords):
                Water(starting_coords=new_coords, chance_to_cascade=chance - CASCADE_CHANCE_REDUCTION)
                break