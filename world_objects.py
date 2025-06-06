import pygame
from random import randrange, random, randint, choice
from utilities.config import *
from utilities.utils import *

# God of all objects, they are made in His image
class Simulation_Object:
    def __init__(self):
        self.grid_pos = (0, 0)
        self.pixel_pos = None
        self.move_to()

        self.energy_value = 0

    def move_to(self, loc: tuple=None) -> None:
        """Moves a simulation object to loc (x,y) on the grid, if no loc provided, random"""
        if not loc:
            while True:
                loc = randrange(0, MAX_GRID_X), randrange(0, MAX_GRID_Y)
                if not tile_occupied(loc):
                    break
        
        self.pixel_pos, self.grid_pos = relocate_object_on_GO(self, loc)

    # def get_grid(self) -> tuple:
    #     """Returns the grid coordinates (x,y) of the object"""
    #     return to_grid(self.current_loc)
    
    def get_grid_distance_to(self, coords: tuple[int, int]) -> int:
        """Gets the grid distance between object and the target"""
        gx, gy = self.grid_pos
        tx, ty = coords
        return abs(gx - tx) + abs(gy - ty)

    def is_adjacent_to(self, coords: tuple[int,int]) -> bool:
        """Checks if the target is adjacent to the object"""
        if not coords:
            return False
        
        tx, ty = coords
        dx, dy = self.grid_pos
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
        self.regrowth_chance = DEFAULT_FOOD_REGROWTH_CHANCE
        self.energy_value = MIN_FOOD_VALUE

    def exist(self, surface):
        if not self.eaten:
            pygame.draw.circle(surface, "red", self.pixel_pos, TILE_SIZE/2)
            self.increase_value()

        # Food regrows, every tick counts the cooldown down 1
        else:
            self.eaten = self.try_to_regrow()

    # Food has to mark itself as eaten :(
    def interact_with(self):
        self.eaten = True
        return super().interact_with()

    def try_to_regrow(self) -> bool:
        if random() < self.regrowth_chance:
            print(f"Food regrew at {self.regrowth_chance*10:.1f}%.")
            self.regrowth_chance = DEFAULT_FOOD_REGROWTH_CHANCE
            self.energy_value = MIN_FOOD_VALUE
            return False
        
        self.regrowth_chance += 0.01
        return True

    def increase_value(self):
        if self.energy_value < MAX_FOOD_VALUE:
            self.energy_value += 1

# Worter
class Water(Simulation_Object):
    _id = 0

    def __init__(self, starting_coords, chance_to_cascade=1):
        super().__init__()
        self.register(Water, WATER, ACTIVE_WATER)
        self.move_to(starting_coords)

        self.energy_value = WATER_VALUE
        
        self.water_positions = []
        self.cascade(chance_to_cascade, starting_coords)

    # Water is a Rect so it requires it's pixel-position to be adjusted by half a grid
    def exist(self, surface):
        offset_position = self.pixel_pos - pygame.Vector2(TILE_SIZE // 2, TILE_SIZE // 2)
        position = pygame.Rect(offset_position, GRID_UNIT)
        pygame.draw.rect(surface, "#47CBED", position)
        self.draw_water(surface) #6DD1EA
    
    # Water attempts to cascade to simulate ponds, rivers, etc.
    # If water cascades, the water it spawns will also attempt to cascade
    def cascade(self, chance, coords):
        if chance <= 0:
            return
        
        if random() <= chance:
            dx, dy = choice(GRID_CARDINALS)
            gx, gy = coords

            new_coords = (gx + dx, gy + dy)

            if tile_occupied(new_coords):
                self.cascade(chance, coords)

            if not tile_occupied(new_coords) and within_bounds(new_coords):
                add_object_to_GO(self, new_coords)
                self.water_positions.append(new_coords)
                self.cascade(chance - CASCADE_CHANCE_REDUCTION, new_coords)

    def draw_water(self, surface):
        for w in self.water_positions:
            offset_position = to_pixel(w) - pygame.Vector2(TILE_SIZE // 2, TILE_SIZE // 2)
            position = pygame.Rect(offset_position, GRID_UNIT)
            pygame.draw.rect(surface, "#5CCFEC", position)