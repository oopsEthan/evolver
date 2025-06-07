import pygame
from utilities.config import *
from utilities.utils import to_grid
from dobs.dobs import Dob
from world_objects import *
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
    
    def run(self) -> None:
        self.initialize_sim()

        is_running = True
        paused = False
        while is_running:
            self.screen.fill("#5FF46F")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        paused = not paused

            if not paused:
                # -- Object-handling --
                self.tick_objects(ACTIVE_WATER)
                self.tick_objects(ACTIVE_TREES)
                self.tick_dobs()

                # -- Debugging --

                # -- End of Drawing --
                pygame.display.flip()

                if len(ACTIVE_DOBS) == 0:
                    is_running = False

                if self.tick % SNAPSHOT_FREQUENCY == 0 and is_running:
                    self.data_collector.generate_snapshot(self.tick)
                
                # -- End of Tick --
                # print(f"End of tick {self.tick}\n")
                self.tick += 1
                self.clock.tick(TPS)

        # -- Post-simulation --
        self.data_collector.save_snapshots_to_file()
        self.data_collector.plot_stats()
        self.data_collector.plot_death_causes()
        self.data_collector.plot_resource_security()
        self.data_collector.plot_alive_vs_food_security()
        pygame.quit()

    # Initializes the simulation by creating all objects
    def initialize_sim(self) -> None:
        self.place_water_sources()
        print(f"Water placed, totaling: {len(ACTIVE_WATER)}")
        self.place_food_trees()
        print(f"Trees placed, totaling: {len(ACTIVE_TREES)}")
        self.populate_dobs()
        print(f"Dobs placed, totaling: {len(ACTIVE_DOBS)}")

    # Places water sources uniformly
    def place_water_sources(self) -> None:
        for _ in range(STARTING_WATER_SOURCES):
            x = int(uniform(0, MAX_GRID_X - 1))
            y = int(uniform(0, MAX_GRID_Y - 1))

            if any(w.grid_pos == (x, y) for w in ACTIVE_WATER):
                continue

            Water(starting_coords=(x, y))

    # Places food trees randomly
    def place_food_trees(self) -> None:
        grid_spacing_x = MAX_GRID_X // 3.5  # 4 = spacing gaps (3 placements)
        grid_spacing_y = MAX_GRID_Y // 3.5

        for i in range(1, 4):  # 1 to 3
            for j in range(1, 4):
                x = i * grid_spacing_x + randint(-2, 2)
                y = j * grid_spacing_y + randint(-2, 2)
                Food_Tree(starting_coords=(x, y))


    # Populates dobs, ensuring an even split of sexes
    def populate_dobs(self) -> None:
        i = 0
        for _ in range(STARTING_DOB_POPULATION):
                sex = FEMALE if i % 2 == 0 else MALE
                Dob(sex)
                i += 1
    
    ## Helper functions
    # Processes non-dob actions per call
    def tick_objects(self, actives: list[Simulation_Object]) -> None:
        for obj in actives:
            obj.exist(self.screen)

    # Processes dob actions per call
    def tick_dobs(self) -> None:
        for dob in ACTIVE_DOBS[:]:
            dob.exist(self.screen)
            if dob.alive == False:
                self.data_collector.process_package(dob.collect_package())
                ACTIVE_DOBS.remove(dob)
    
    ## Debug functions
    # Draws grid on screen with grid coordinates
    def _draw_grid_DEBUG(self) -> None:
        font = pygame.font.SysFont(None, 18)
        grid_color = (40, 40, 40)
        label_color = (0, 0, 0)

        for x in range(0, MAX_X, TILE_SIZE):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, MAX_Y))
            grid_index = x // TILE_SIZE
            label = font.render(str(grid_index), True, label_color)
            self.screen.blit(label, (x + 2, 2))

        for y in range(0, MAX_Y, TILE_SIZE):
            pygame.draw.line(self.screen, grid_color, (0, y), (MAX_X, y))
            grid_index = y // TILE_SIZE
            label = font.render(str(grid_index), True, label_color)
            self.screen.blit(label, (2, y + 2))
    
    # Draws paths created in pathfinding (call on dobs)
    def _draw_path_DEBUG(self, obj):
        if obj.current_path:
            for i in range(len(obj.current_path) - 1):
                start = obj.current_path[i]
                end = obj.current_path[i + 1]
                pygame.draw.line(self.screen, "black", to_pixel(start), to_pixel(end))

            final_tile = obj.current_path[-1]
            offset = to_pixel(final_tile) - pygame.Vector2(TILE_SIZE // 2, TILE_SIZE // 2)
            pygame.draw.rect(self.screen, "red", pygame.Rect(offset, GRID_UNIT))


simulator = Simulator()
simulator.run()