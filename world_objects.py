import pygame
from random import randrange
from config import MAX_X, MAX_Y, CELL_SIZE

class Food():
    _id = 0

    def __init__(self):
        self.id = Food._id
        Food._id += 1

        self.random_spawn()
        self.eaten = False

    def random_spawn(self):
        spawn_x = randrange(0, MAX_X, CELL_SIZE) + CELL_SIZE // 2
        spawn_y = randrange(0, MAX_Y, CELL_SIZE) + CELL_SIZE // 2
        self.current_location = pygame.Vector2(spawn_x, spawn_y)
    
    def exist(self, surface):
        pygame.draw.circle(surface, "red", self.current_location, CELL_SIZE/2)
    
    def get_grid_location(self):
        grid_x = int(self.current_location.x // CELL_SIZE)
        grid_y = int(self.current_location.y // CELL_SIZE)

        return grid_x, grid_y