import pygame
from random import randrange
from config import MAX_X, MAX_Y, CELL_SIZE, FOOD, WATER

class Simulation_Object:
    def __init__(self):
        self.current_location = pygame.Vector2(0, 0)
        self.energy_value = 0
    
    def spawn(self, loc="random"):
        if loc == "random":
            spawn_x = randrange(0, MAX_X, CELL_SIZE) + CELL_SIZE // 2
            spawn_y = randrange(0, MAX_Y, CELL_SIZE) + CELL_SIZE // 2
            self.current_location = pygame.Vector2(spawn_x, spawn_y)

    def get_grid_coordinates(self):
        grid_x = int(self.current_location.x // CELL_SIZE)
        grid_y = int(self.current_location.y // CELL_SIZE)
        return grid_x, grid_y
    
    def get_grid_distance_between(self, target):
        dx = abs(int(self.current_location.x // CELL_SIZE) - target[0])
        dy = abs(int(self.current_location.y // CELL_SIZE) - target[1])
        return dx + dy

    def interact_with(self, interaction=""):
        if interaction == "eat":
            return self.energy_value
    
class Food(Simulation_Object):
    _id = 0

    def __init__(self):
        super().__init__()
        self.id = Food._id
        Food._id += 1

        self.consumed = False
        self.object_tag = FOOD
        self.energy_value = 250

        self.spawn()
    
    def exist(self, surface):
        pygame.draw.circle(surface, "red", self.current_location, CELL_SIZE/2)

    def interact_with(self, interaction="eat"):
        self.consumed = True
        return super().interact_with(interaction)
    
class Water(Simulation_Object):
    _id = 0

    def __init__(self):
        super().__init__()
        self.id = Water._id
        Water._id += 1

        self.object_tag = WATER
        self.energy_value = 10

        self.spawn()
    
    def exist(self, surface):
        # Gotta find a way to make this look more like real water or at least spread it out
        pixel_position = self.current_location - pygame.Vector2(CELL_SIZE // 2, CELL_SIZE // 2)
        water_source = pygame.Rect(pixel_position, (CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(surface, "#47CBED", water_source)