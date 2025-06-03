import pygame
from config import *
from dobs.dobs import Dob
from world_objects import Food, Water
from random import choice, uniform
from data.data_collector import Data_Collector

class Simulator():
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Evolver")
        self.screen = pygame.display.set_mode((MAX_X, MAX_Y))
        self.clock = pygame.time.Clock()
        self.debug_call = 20
        self.tick = 0

        self.data_collector = Data_Collector()
    
    def run(self):
        self.is_running = True
        self.place_water()
        self.place_food()
        self.populate()

        while self.is_running:
            self.screen.fill("#5FF46F")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
            
            for dob in ACTIVE_DOBS:
                dob.exist(self.screen)
                if dob.alive == False:
                    self.data_collector.report(DOB, dob.collect_package())
                    ACTIVE_DOBS.remove(dob)
            
            for food in ACTIVE_FOOD:
                food.exist(self.screen)

            for water in ACTIVE_WATER:
                water.exist(self.screen)

            # Debug
            self.debug_draw_grid(False) # Draws grid if 'True'

            pygame.display.flip()

            if len(ACTIVE_FOOD) < STARTING_FOOD_COUNT:
                self.place_food(1)

            if self.debug_call == 10:
                for dob in ACTIVE_DOBS:
                    dob.debug_return_state()
                    self.debug_call = 0

            self.debug_call += 1
            self.clock.tick(FPS)

            if len(ACTIVE_DOBS) == 0:
                print(f"All dobs have died! Simulation lasted {self.tick} ticks!")
                self.is_running = False
        
            if self.tick % SNAPSHOT_FREQUENCY == 0:
                print(f"Generating snapshot at {self.tick}...")
                self.data_collector.generate_snapshot()
            
            # <- End of tick
            self.tick += 1

        # <- Once simulation ends
        self.data_collector.generate_snapshot()
        self.data_collector.save_to_data_file()
        pygame.quit()
    
    def populate(self):
        i = 0
        for _ in range(STARTING_DOB_POPULATION):
                sex = "F" if i % 2 == 0 else "M"
                dob = Dob(sex)
                dob.place()
                i += 1
    
    def place_food(self, food_placed=STARTING_FOOD_COUNT):
        for _ in range(food_placed):
            food = Food()
            ACTIVE_FOOD.append(food)
    
    def place_water(self):
        grid_width = MAX_X // CELL_SIZE
        grid_height = MAX_Y // CELL_SIZE

        for _ in range(STARTING_WATER_SOURCES):
            x = int(uniform(0, grid_width - 1))
            y = int(uniform(0, grid_height - 1))

            if any(w.get_grid_coordinates() == (x, y) for w in ACTIVE_WATER):
                continue

            water = Water(starting_coords=(x,y))
            ACTIVE_WATER.append(water)

    # Debugging Functions
    def debug_draw_grid(self, draw):
        if draw:
            font = pygame.font.SysFont(None, 18)
            grid_color = (40, 40, 40)
            label_color = (0, 0, 0)

            for x in range(0, MAX_X, CELL_SIZE):
                pygame.draw.line(self.screen, grid_color, (x, 0), (x, MAX_Y))
                grid_index = x // CELL_SIZE
                label = font.render(str(grid_index), True, label_color)
                self.screen.blit(label, (x + 2, 2))

            for y in range(0, MAX_Y, CELL_SIZE):
                pygame.draw.line(self.screen, grid_color, (0, y), (MAX_X, y))
                grid_index = y // CELL_SIZE
                label = font.render(str(grid_index), True, label_color)
                self.screen.blit(label, (2, y + 2))


simulator = Simulator()
simulator.run()