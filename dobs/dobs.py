import pygame
from random import choice
from utilities.config import *
from utilities.utils import *
from dobs.brain import Brain
from world_objects import Simulation_Object

class Dob(Simulation_Object):
    _id = 0

    def __init__(self, sex=choice(["F", "M"]), mom=None, dad=None):
        super().__init__()
        self.register(Dob, DOB, ACTIVE_DOBS)
        self.generate_biology(sex, mom, dad)
        self.generate_needs()

    ## Main functions
    # Called each tick to handle behavior, cooldowns, aging, and rendering
    def exist(self, surface):
        self.brain.age_memories()
        self.see()
        self.brain.think()

        if self.age >= DOB_DEATH_AGE:
            self.die()
        
        self.increment()
        pygame.draw.circle(surface, self.color, self.current_loc, CELL_SIZE/2)

    # Moves dob to target's grid coordinates, if target=None, move randomly
    def move_towards(self, target=None):
        current_x, current_y = self.get_grid()

        if target:
            tx, ty = target.get_grid()
            dx = tx - current_x
            dy = ty - current_y

            if abs(dx) > abs(dy):
                direction = EAST if dx > 0 else WEST
            else:
                direction = NORTH if dy > 0 else SOUTH

        else:
            directions = GRID_CARDINALS + GRID_DIAGONALS
            direction = choice(directions)

        dest_x = current_x + direction[0]
        dest_y = current_y + direction[1]
        destination = (dest_x, dest_y)

        if self.within_bounds(destination):
            super().move_to(destination)
            self.expend_energy(1)

    # Defines a variety of actions based on the object (target) being interacted with
    def interact(self, target):
        if target.tag == FOOD:
            self.current_calories += target.interact_with()
        
        elif target.tag == WATER:
            self.brain.memorize(LONG_TERM, target)
            self.thirst_threshhold = 0.4
            self.current_hydration += target.interact_with()

        elif target.tag == DOB:
            self.mate(target)

        return True
    
    # Calculates all visible tiles within sight distance and then passes visible tiles to memory
    def see(self):
        grid_x, grid_y = self.get_grid()
        sight_distance = self.dna["sight"]
        visible_tiles = []

        for x in range(grid_x - sight_distance, grid_x + sight_distance + 1):
            for y in range(grid_y - sight_distance, grid_y + sight_distance + 1):
                if 0 <= x < MAX_GRID_X and 0 <= y < MAX_GRID_Y:
                    visible_tiles.append((x, y))

        self.memorize_interests(visible_tiles)

    # When dobs do something that requires energy, this is called to expend it
    def expend_energy(self, factor):
        self.current_calories -= 10 * factor
        self.current_hydration -= 1 * factor

        if self.current_calories == 0 or self.current_hydration == 0:
            self.die()
    
    # Mating creates a new dob with a combo of mom and dad's stats
    # Mating is only possible if both dobs are mating age and not on cooldown
    def mate(self, target):
        female, male = (target, self) if target.sex == "F" else (self, target)

        if target.can_mate():
            dob = Dob(mom=female, dad=male)
            dob.move_to(female.get_grid())

            female.mating_cooldown = MATING_COOLDOWN
            female.expend_energy(5)
            female.offspring += 1

            male.mating_cooldown = MATING_COOLDOWN
            male.expend_energy(3)

            return
        
        self.mating_cooldown += MATING_COOLDOWN/2
    
    # Defines a dob's cause of death and sets them to dead - RIP
    def die(self):
        if self.age >= DOB_TRAITS["DEATH_AGE"]:
            self.cause_of_death = "age"

        elif self.current_calories <= 0:
            self.cause_of_death = "starvation"

        elif self.current_hydration <= 0:
            self.cause_of_death = "dehydration"
        
        self.alive = False

    ## Data functions
    # Collects dob's information and returns it
    def collect_package(self):
        package = {}

        if self.cause_of_death:
            package["cause_of_death"] = self.cause_of_death
        
        return package
    
    ## Helper functions
    # Defines all of the dob's starting 'biological' traits
    def generate_biology(self, sex, mom, dad):
        # Brain
        self.brain = Brain()
        self.brain.dob = self
        self.alive = True

        # Sex
        self.sex = sex
        self.color = DOB_TRAITS[sex]

        self.mating_cooldown = MATING_COOLDOWN
        self.age = 0
        self.offspring = 0
        self.cause_of_death = ""
        
        self.dna = {
            "sight": 3,
            "max_calories": 1000,
            "max_hydration": 100,
        }

    # Defines all of the dob's starting needs
    def generate_needs(self):
        self.current_calories = self.dna["max_calories"]
        self.hunger_threshhold = 0.8
        self.current_hydration = self.dna["max_hydration"]
        self.thirst_threshhold = 0.8

    # Checks hunger
    def is_hungry(self) -> bool:
        return self.current_calories < (self.dna["max_calories"] * self.hunger_threshhold)
    
    # Checks thirst
    def is_thirsty(self) -> bool:
        return self.current_hydration < (self.dna["max_hydration"] * self.thirst_threshhold)

    # Checks ability to mate
    def can_mate(self) -> bool:
        return (self.mating_cooldown == 0 and
                self.age >= MATING_AGE and
                self.current_calories > self.dna["max_calories"] * self.hunger_threshhold and
                self.current_hydration > self.dna["max_hydration"] * self.thirst_threshhold)
    
    # Scans visible tiles and memorizes any food, water, or dobs found
    def memorize_interests(self, tiles):
        interests = [ACTIVE_WATER, ACTIVE_FOOD, ACTIVE_DOBS]

        for interest in interests:
            for obj in interest:
                if obj is self:
                    continue
                if obj.get_grid() in tiles:
                    self.brain.memorize(SHORT_TERM, obj)

    # Increments counters
    def increment(self):
        if self.mating_cooldown > 0:
                self.mating_cooldown -= MATING_COOLDOWN_SPEED

        self.age += AGE_RATE