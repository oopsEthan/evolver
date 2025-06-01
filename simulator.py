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
        self.debug_call = 20
        self.year = 0
    
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

            if len(ACTIVE_FOOD) < STARTING_FOOD_COUNT:
                self.place_food(1)

            if self.debug_call == 10:
                for dob in ACTIVE_DOBS:
                    dob.debug_return_state()
                    self.debug_call = 0

            self.year += 1
            self.debug_call += 1
            self.clock.tick(FPS)

            if len(ACTIVE_DOBS) == 0:
                print(f"All dobs have died! Simulation lasted {self.year} ticks!")
                self.is_running = False
        
        pygame.quit()
    
    def populate(self):
        for _ in range(STARTING_DOB_POPULATION):
                dob = Dob()
                dob.spawn()
                ACTIVE_DOBS.append(dob)
    
    def place_food(self, food_placed=STARTING_FOOD_COUNT):
        for _ in range(food_placed):
            food = Food()
            ACTIVE_FOOD.append(food)

    def place_water(self):
        for _ in range(STARTING_WATER_SOURCES):
            water = Water()
            ACTIVE_WATER.append(water)

    def draw_grid(self):
        for x in range(0, MAX_X, CELL_SIZE):
            pygame.draw.line(self.screen, (40, 40, 40), (x, 0), (x, MAX_Y))
        for y in range(0, MAX_Y, CELL_SIZE):
            pygame.draw.line(self.screen, (40, 40, 40), (0, y), (MAX_X, y))

simulator = Simulator()
simulator.run()