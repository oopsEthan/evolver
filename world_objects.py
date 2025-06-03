import pygame
from random import randrange, random, choice
from utilities.config import MAX_X, MAX_Y, CELL_SIZE, FOOD, FOOD_REGROWTH_RATE, WATER, ACTIVE_WATER, GRID_CARDINALS
from utilities.utils import to_pixel, to_grid

class Simulation_Object:
    def __init__(self):
        self.current_loc = pygame.Vector2(0, 0)
        self.energy_value = 0
    
    # Places a simulation object at loc (x,y) on the grid, if no loc provided, random
    def place(self, loc=None):
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
        gx, gy = self.get_grid_coordinates()
        tx, ty = target
        return abs(gx - tx) + abs(gy, ty)

    # Indicate what happens when a dob interacts with the object, by default it returns an energy value
    def interact_with(self):
        return self.energy_value
    
    # Check to see if the destination is within bounds, accepts (grid_x, grid_y)
    def within_bounds(self, destination):
        x, y = destination
        return 0 <= x < to_grid(MAX_X) and 0 <= y < to_grid(MAX_Y)
    
class Food(Simulation_Object):
    _id = 0

    def __init__(self):
        super().__init__()
        self.id = Food._id
        Food._id += 1

        self.consumed = False
        self.object_tag = FOOD
        self.regrowth = 0
        self.energy_value = 250

        self.place()
    
    def exist(self, surface):
        if not self.consumed:
            pygame.draw.circle(surface, "red", self.current_loc, CELL_SIZE/2)

        else:
            if self.regrowth == FOOD_REGROWTH_RATE:
                self.consumed = False
                self.regrowth = 0
            
            self.regrowth += 1

    def interact_with(self, interaction="eat"):
        self.consumed = True
        return super().interact_with(interaction)
    
class Water(Simulation_Object):
    _id = 0

    def __init__(self, source=False, cascade_chance=1, starting_coords=None):
        super().__init__()
        self.id = Water._id
        Water._id += 1

        ACTIVE_WATER.append(self)

        self.object_tag = WATER
        self.energy_value = 25
        self.chance_to_cascade = cascade_chance

        if source:
            self.place(starting_coords)
            self.cascade()

    # Water is a Rect so it requires it's pixel-position to be adjusted by half a grid
    def exist(self, surface):
        offset_position = self.current_loc - pygame.Vector2(CELL_SIZE // 2, CELL_SIZE // 2)
        position = pygame.Rect(offset_position, (CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(surface, "#47CBED", position)

    # Water attempts to cascade to simulate ponds, rivers, etc.
    # If water cascades, the water it spawns will also attempt to cascade
    def cascade(self):
        directions = GRID_CARDINALS
        
        if random() <= self.chance_to_cascade:
            direction = choice(directions)

            gx, gy = self.get_grid()
            new_coords = (gx + direction[0], gy + direction[1])

            if not self.within_bounds(new_coords):
                return

            # If water exists, attempt to cascade again
            for obj in ACTIVE_WATER:
                if obj.get_grid() == new_coords:
                    self.cascade()
                    return

            water = Water(, cascade_chance=self.chance_to_cascade - 0.02)
            water.place(new_coords)
            water.cascade()