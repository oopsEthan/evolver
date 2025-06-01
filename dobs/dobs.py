import pygame
from random import randrange, choice
from config import *
from dobs.brain import Brain
from world_objects import Simulation_Object

class Dob(Simulation_Object):
    _id = 0

    def __init__(self):
        super().__init__()
        self.id = Dob._id
        Dob._id += 1

        self.object_tag = "dob"

        self.brain = Brain()
        self.brain.dob = self

        self.alive = True
        self.sex = choice(["F", "M"])
        
        self.dna = {
            "sight": 2,
            "max_calories": 1000,
            "max_hydration": 50,
        }

        self.current_calories = self.dna["max_calories"] * 0.8
        self.current_hydration = self.dna["max_hydration"]

        self.spawn()

    # Movement
    def move_to(self, target=None):
        if not target:
            x_change = randrange(-1, 2) * CELL_SIZE
            y_change = randrange(-1, 2) * CELL_SIZE

            destination = self.current_location + pygame.Vector2(x_change, y_change)

        if target:
            tx, ty = target["grid_loc"]
            dx, dy = self.get_grid_coordinates()

            move_x = tx - dx
            move_y = ty - dy

            if abs(move_x) > abs(move_y):
                step = pygame.Vector2(CELL_SIZE if move_x > 0 else -CELL_SIZE, 0)
            else:
                step = pygame.Vector2(0, CELL_SIZE if move_y > 0 else -CELL_SIZE)

            destination = self.current_location + step

        if 0 <= destination.x < MAX_X and 0 <= destination.y < MAX_Y:
            self.current_location = destination
        
        self.expend_energy(1)

    def interact(self, target):
            if target.object_tag == FOOD:
                self.current_calories += target.interact_with("eat")
            
            elif target.object_tag == WATER:
                self.current_hydration += target.interact_with("eat")

            return True
    
    def see(self):
        grid_x = int(self.current_location.x // CELL_SIZE)
        grid_y = int(self.current_location.y // CELL_SIZE)
        sight_distance = self.dna["sight"]

        interests = [
            ("need", ACTIVE_FOOD),
            ("need", ACTIVE_WATER),
            ("dob", ACTIVE_DOBS)
        ]

        visible_tiles = []

        for x in range(grid_x - sight_distance, grid_x + sight_distance + 1):
            for y in range(grid_y - sight_distance, grid_y + sight_distance + 1):
                if 0 <= x < MAX_X // CELL_SIZE and 0 <= y < MAX_Y // CELL_SIZE:
                    visible_tiles.append((x, y))

        for interest_type, interest_object in interests:
            for object in interest_object:
                if object.get_grid_coordinates() in visible_tiles:
                    memory = {
                        "type": interest_type,
                        "need_type": object.object_tag,
                        "object": object,
                        "grid_loc": object.get_grid_coordinates()
                    }
                        
                    self.brain.memorize(self, "short", memory)
                    print(f"Dob #{self.id} spotted a '{interest_type}' at {object.get_grid_coordinates()}!")

        return visible_tiles

    def expend_energy(self, factor):
        self.current_calories -= 10 * factor
        self.current_hydration -= 1 * factor

        if self.current_calories == 0 or self.current_hydration == 0:
            # self.alive = False
            pass
        
    def exist(self, surface):
        pygame.draw.circle(surface, DOB_TRAITS[self.sex], self.current_location, CELL_SIZE/2)
        self.brain.forget()
        self.see()
        self.brain.think()
    
    def move(self, destination) -> bool:
        if 0 <= destination.x < MAX_X and 0 <= destination.y < MAX_Y:
            self.current_location = destination
            self.expend_energy(1)
            return True
        return False
    
    def check(self, req):
        if req == FOOD:
            return self.current_calories < self.dna["max_calories"] * 0.8
        elif req == WATER:
            return self.current_hydration < self.dna["max_hydration"]

        return False