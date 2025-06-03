import pygame
from utilities.config import *
from utilities.utils import to_grid
from dobs.dobs import Dob
from world_objects import Food, Water
from random import uniform
from data.data_collector import Data_Collector

class Simulator():
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Evolver")
        self.screen = pygame.display.set_mode((MAX_X, MAX_Y))

        self.clock = pygame.time.Clock()
        self.tick = 0

        self.data_collector = Data_Collector()
    
    def run(self):
        self.initialize_sim()

        is_running = True
        while is_running:
            self.screen.fill("#5FF46F")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False

            for water in ACTIVE_WATER:
                water.exist(self.screen)

            for dob in ACTIVE_DOBS[:]:
                dob.exist(self.screen)
                if dob.alive == False:
                    self.data_collector.report(DOB, dob.collect_package())
                    ACTIVE_DOBS.remove(dob)
            
            for food in ACTIVE_FOOD:
                food.exist(self.screen)

            # Debugging
            self.debug_draw_grid(False) # Draws grid if 'True'

            # <- Drawing done before here
            pygame.display.flip()

            self.clock.tick(FPS)

            if len(ACTIVE_DOBS) == 0:
                break

            if self.tick % SNAPSHOT_FREQUENCY == 0:
                self.data_collector.generate_snapshot()
            
            # <- End of tick
            self.tick += 1

        # <- Once simulation ends
        self.data_collector.generate_snapshot()
        self.data_collector.save_to_data_file()
        pygame.quit()
    
    # Populates dobs, ensuring an even split of sexes
    def populate_dobs(self):
        i = 0
        for _ in range(STARTING_DOB_POPULATION):
                sex = "F" if i % 2 == 0 else "M"
                dob = Dob(sex)
                i += 1
    
    # Places food randomly
    def place_food(self):
        for _ in range(STARTING_FOOD_COUNT):
            Food()
    
    # Places water sources
    def place_water_sources(self):
        for _ in range(STARTING_WATER_SOURCES):
            x = int(uniform(0, MAX_GRID_X - 1))
            y = int(uniform(0, MAX_GRID_Y - 1))

            if any(w.get_grid() == (x, y) for w in ACTIVE_WATER):
                continue

            Water(starting_coords=(x,y))

    # Initializes the simulation by creating all objects
    def initialize_sim(self):
        self.place_water_sources()
        self.place_food()
        self.populate_dobs()
        
    ## DEBUGGING
    # When True, draws grid on screen
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