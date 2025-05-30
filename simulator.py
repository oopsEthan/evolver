import pygame
from config import *
from dobs.dobs import Dob
from world_objects import Food, Water
from random import choice

class Simulator():
    def __init__(self, grid=False):
        pygame.init()
        self.grid = grid
        self.screen = pygame.display.set_mode((MAX_X, MAX_Y))
        self.clock = pygame.time.Clock()
    
    def run(self):
        self.is_running = True
        self.place_water()
        self.place_food()
        self.populate()

        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False

            self.screen.fill("#5FF46F")
            if self.grid:
                self.draw_grid()
            
            for dob in ACTIVE_DOBS:
                dob.exist(self.screen)
            
            for food in ACTIVE_FOOD:
                food.exist(self.screen)

            for water in ACTIVE_WATER:
                water.exist(self.screen)

            pygame.display.flip()

            ACTIVE_DOBS[:] = [dob for dob in ACTIVE_DOBS if dob.alive]
            ACTIVE_FOOD[:] = [food for food in ACTIVE_FOOD if not food.consumed]
            self.clock.tick(FPS)
        
        pygame.quit()
    
    def populate(self):
        for _ in range(STARTING_DOB_POPULATION):
                dob = Dob()
                print(f"Dob #{dob.id} created!")
                ACTIVE_DOBS.append(dob)
    
    def place_food(self):
        for _ in range(STARTING_FOOD_COUNT):
            food = Food()
            print(f"Food placed: {food.get_grid_coordinates()}")
            ACTIVE_FOOD.append(food)

    def place_water(self):
        for _ in range(STARTING_WATER_SOURCES):
            water = Water()
            print(f"Water source placed: {water.get_grid_coordinates()}")
            ACTIVE_WATER.append(water)

    def draw_grid(self):
        for x in range(0, MAX_X, CELL_SIZE):
            pygame.draw.line(self.screen, (40, 40, 40), (x, 0), (x, MAX_Y))
        for y in range(0, MAX_Y, CELL_SIZE):
            pygame.draw.line(self.screen, (40, 40, 40), (0, y), (MAX_X, y))

simulator = Simulator()
simulator.run()