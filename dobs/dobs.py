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

        self.object_tag = DOB

        self.brain = Brain()
        self.brain.dob = self
        self.toggle = True
        self.alive = True
        self.sex = choice(["F", "M"])
        self.sex_drive = 0
        self.age = 0
        
        self.dna = {
            "sight": 3,
            "max_calories": 1000,
            "max_hydration": 100,
        }

        self.current_calories = self.dna["max_calories"]
        self.hunger_threshhold = 0.8
        self.current_hydration = self.dna["max_hydration"]
        self.thirst_threshhold = 0.8

    # Movement
    def move_to(self, target=None):
        if not target:
            directions = [
                pygame.Vector2(CELL_SIZE, 0),
                pygame.Vector2(-CELL_SIZE, 0),
                pygame.Vector2(0, CELL_SIZE),
                pygame.Vector2(0, -CELL_SIZE),
                pygame.Vector2(CELL_SIZE, -CELL_SIZE),
                pygame.Vector2(-CELL_SIZE, -CELL_SIZE),
                pygame.Vector2(-CELL_SIZE, CELL_SIZE),
                pygame.Vector2(CELL_SIZE, CELL_SIZE)
            ]

            step = choice(directions)
            destination = self.current_location + step

        if target:
            tx, ty = target.get_grid_coordinates()
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
                self.brain.memorize("long", target)
                self.thirst_threshhold = 0.4
                self.current_hydration += target.interact_with("eat")

            elif target.object_tag == DOB:
                print("Attempting interaction with a dob!")
                self.mate(target)

            return True
    
    def see(self):
        grid_x = int(self.current_location.x // CELL_SIZE)
        grid_y = int(self.current_location.y // CELL_SIZE)
        sight_distance = self.dna["sight"]

        interests = [ACTIVE_WATER, ACTIVE_FOOD, ACTIVE_DOBS]

        visible_tiles = []

        for x in range(grid_x - sight_distance, grid_x + sight_distance + 1):
            for y in range(grid_y - sight_distance, grid_y + sight_distance + 1):
                if 0 <= x < MAX_X // CELL_SIZE and 0 <= y < MAX_Y // CELL_SIZE:
                    visible_tiles.append((x, y))

        for interest in interests:
            for object in interest:
                if object is self:
                    continue
                if object.get_grid_coordinates() in visible_tiles:
                    self.brain.memorize("short", object)

        return visible_tiles

    def expend_energy(self, factor):
        self.current_calories -= 10 * factor
        self.current_hydration -= 1 * factor

        if self.current_calories == 0 or self.current_hydration == 0:
            self.die()
        
    def exist(self, surface):
        pygame.draw.circle(surface, DOB_TRAITS[self.sex], self.current_location, CELL_SIZE/2)

        if self.sex_drive < DEFAULT_SEX_DRIVE:
            self.sex_drive += 1

        self.brain.forget()
        self.see()
        self.brain.think()

        self.age += 1
        if self.age >= DOB_TRAITS["DEATH_AGE"]:
            self.die()

        if self.age >= MATING_AGE and self.sex_drive >= DEFAULT_SEX_DRIVE and self.toggle:
            self.toggle = False
    
    def mate(self, target):
        female = target if target.sex == "F" else self

        if target.sex_drive >= DEFAULT_SEX_DRIVE and target.age >= MATING_AGE:
            dob = Dob()
            dob.spawn(female.get_grid_coordinates())
            print(f"Dob #{self.id} and Dob #{target.id} procreated, giving birth to Dob #{dob.id}!")
            ACTIVE_DOBS.append(dob)

            target.sex_drive = 0
            target.expend_energy(5)
            self.sex_drive = 0
            self.expend_energy(3)
        
        else:
            print(f"Reproduction failed, dob #{self.id}: '{self.sex_drive}', '{self.age}' and dob #{target.id}: '{target.sex_drive}', '{target.age}'")

    def check(self, req):
        if req == FOOD:
            return self.current_calories < self.dna["max_calories"] * self.hunger_threshhold
        elif req == WATER:
            return self.current_hydration < self.dna["max_hydration"] * self.thirst_threshhold
        elif req == REPRODUCTION and self.age >= MATING_AGE:
            return self.current_calories > self.dna["max_calories"] * 0.4 and self.current_hydration > self.dna["max_hydration"] * 0.4
        
        return False
    
    def die(self):
        if self.age >= DOB_TRAITS["DEATH_AGE"]:
            print(f"Dob #{self.id} died of old age. Age='{self.age}'")

        elif self.current_calories <= 0:
            print(f"Dob #{self.id} died of starvation!")
            self.debug_return_state()

        elif self.current_hydration <= 0:
            print(f"Dob #{self.id} died of dehydration!")
            self.debug_return_state()
        
        self.alive = False

    def debug_return_state(self):
        print(f"Dob #{self.id}, status: '{self.sex}', 'calories'={self.current_calories}, 'hydration'={self.current_hydration}, 'reproduction'={self.check(REPRODUCTION)}")