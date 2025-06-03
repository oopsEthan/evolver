import pygame
from random import randrange, random, choice
from utilities.config import *
from utilities.utils import to_pixel, to_grid

# God of all objects, they are made in His image
class Simulation_Object:
    def __init__(self, starting_coords=None):
        self.move_to(starting_coords)
        self.energy_value = 0

    # Moves a simulation object to loc (x,y) on the grid, if no loc provided, random
    def move_to(self, loc=None):
        if not loc:
            spawn_x = to_pixel(randrange(0, MAX_X, CELL_SIZE))
            spawn_y = to_pixel(randrange(0, MAX_Y, CELL_SIZE))

        if loc:
            spawn_x, spawn_y = to_pixel(loc)
        
        self.current_loc = pygame.Vector2(spawn_x, spawn_y)

    # Returns the grid coordinates (x,y) of the object
    def get_grid(self):
        return to_grid(self.current_loc)
    
    # Gets the grid distance between object and the target
    def get_grid_distance_between(self, target):
        gx, gy = self.get_grid()
        tx, ty = target
        return abs(gx - tx) + abs(gy - ty)

    # Indicate what happens when a dob interacts with the object, by default it returns an energy value
    def interact_with(self):
        return self.energy_value
    
    # Check to see if the destination is within bounds, accepts grid coords
    def within_bounds(self, destination):
        x, y = destination
        return 0 <= x < to_grid(MAX_X) and 0 <= y < to_grid(MAX_Y)

    # Registers the object to the simulation
    def register(self, object_class, object_tag, db):
        self.id = object_class._id
        object_class._id += 1

        self.tag = object_tag
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
            pygame.draw.circle(surface, "red", self.current_loc, CELL_SIZE/2)

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

    def __init__(self, chance_to_cascade=1):
        super().__init__()
        self.register(Water, WATER, ACTIVE_WATER)

        self.energy_value = WATER_VALUE
        
        self.cascade(chance_to_cascade)

    # Water is a Rect so it requires it's pixel-position to be adjusted by half a grid
    def exist(self, surface):
        offset_position = self.current_loc - pygame.Vector2(CELL_SIZE // 2, CELL_SIZE // 2)
        position = pygame.Rect(offset_position, (CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(surface, "#47CBED", position)
    
    # Water attempts to cascade to simulate ponds, rivers, etc.
    # If water cascades, the water it spawns will also attempt to cascade
    def cascade(self, chance):
        directions = GRID_CARDINALS
        
        if chance <= 0:
            return
        
        if random() <= chance:
            target_x, target_y = choice(directions)

            grid_x, grid_y = self.get_grid()
            new_coords = (grid_x + target_x, grid_y + target_y)

            if not self.within_bounds(new_coords):
                return

            # If water exists in cascade spot, attempt to cascade again
            for obj in ACTIVE_WATER:
                if obj.get_grid() == new_coords:
                    self.cascade(chance)
                    return

            Water(starting_coords=new_coords, chance_to_cascade=chance-CASCADE_CHANCE_REDUCTION)