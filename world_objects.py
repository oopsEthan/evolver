import pygame
from random import randrange
from config import MAX_X, MAX_Y, CELL_SIZE

class Simulation_Object:
    def __init__(self):
        self.current_location = pygame.Vector2(0, 0)
    
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

    
class Food(Simulation_Object):
    _id = 0

    def __init__(self):
        super().__init__()
        self.id = Food._id
        Food._id += 1
        self.consumed = False
        self.caloric_category = "food"

        self.spawn()
    
    def exist(self, surface):
        pygame.draw.circle(surface, "red", self.current_location, CELL_SIZE/2)

    def absorb(self):
        self.consumed = True
        caloric_output = 250
        return caloric_output, self.caloric_category
    
class Water(Simulation_Object):
    _id = 0

    def __init__(self):
        super().__init__()
        self.id = Water._id
        Water._id += 1
        self.caloric_category = "water"

        self.spawn()
    
    def exist(self, surface):
        # Gotta find a way to make this look more like real water or at least spread it out
        pixel_position = self.current_location - pygame.Vector2(CELL_SIZE // 2, CELL_SIZE // 2)
        water_source = pygame.Rect(pixel_position, (CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(surface, "#47CBED", water_source)

    def absorb(self):
        caloric_output = 10
        return caloric_output, self.caloric_category