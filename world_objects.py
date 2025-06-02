import pygame
from random import randrange, random, choice
from config import MAX_X, MAX_Y, CELL_SIZE, FOOD, FOOD_REGROWTH_RATE, WATER, ACTIVE_WATER

class Simulation_Object:
    def __init__(self):
        self.current_location = pygame.Vector2(0, 0)
        self.energy_value = 0
    
    def spawn(self, loc=None):
        if not loc:
            spawn_x = randrange(0, MAX_X, CELL_SIZE) + CELL_SIZE // 2
            spawn_y = randrange(0, MAX_Y, CELL_SIZE) + CELL_SIZE // 2

        else:
            spawn_x = loc[0] * CELL_SIZE + CELL_SIZE // 2
            spawn_y = loc[1] * CELL_SIZE + CELL_SIZE // 2
        
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
        self.regrowth = 0
        self.energy_value = 250

        self.spawn()
    
    def exist(self, surface):
        if not self.consumed:
            pygame.draw.circle(surface, "red", self.current_location, CELL_SIZE/2)

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

    def __init__(self, from_cascade=False, cascade_chance=1, starting_coords=None):
        super().__init__()
        self.id = Water._id
        Water._id += 1

        self.object_tag = WATER
        self.energy_value = 25
        self.chance_to_cascade = cascade_chance

        if not from_cascade:
            self.spawn(starting_coords)
            self.cascade()
    
    def exist(self, surface):
        # Gotta find a way to make this look more like real water or at least spread it out
        pixel_position = self.current_location - pygame.Vector2(CELL_SIZE // 2, CELL_SIZE // 2)
        water_source = pygame.Rect(pixel_position, (CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(surface, "#47CBED", water_source)

    def cascade(self):
        directions = [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1)
        ]

        if random() <= self.chance_to_cascade:
            direction = choice(directions)

            gx, gy = self.get_grid_coordinates()
            print(f"Source at: {self.get_grid_coordinates()}")
            new_coords = (gx + direction[0], gy + direction[1])

            if not (0 <= new_coords[0] < MAX_X // CELL_SIZE and 0 <= new_coords[1] < MAX_Y // CELL_SIZE):
                return

            for obj in ACTIVE_WATER:
                if obj.get_grid_coordinates() == new_coords:
                    return

            water = Water(from_cascade=True, cascade_chance=self.chance_to_cascade - 0.02)
            water.spawn(new_coords)
            ACTIVE_WATER.append(water)
            print(f"Water cascade started at {new_coords}!")

            water.cascade()
