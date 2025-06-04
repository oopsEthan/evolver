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

        self.current_path = []

    ## Main functions
    # Called each tick to handle behavior, cooldowns, aging, and rendering
    def exist(self, surface):
        pygame.draw.circle(surface, self.color, self.current_loc, self.size)

        return
        self.see()
        self.brain.think()

        self.increment()

    # Moves dob to target's grid coordinates, if target=None, move randomly
    def move_towards(self, target=None) -> bool:
        if not target:
            self.current_path = self.find_path(self.get_grid(), self.get_random_tile())

        if not self.current_path and target:
            self.current_path = self.find_path(self.get_grid(), target.get_grid())
        
        next_step = self.current_path[0]

        if tile_available(next_step):
            self.move_to(next_step)
            self.current_path.pop(0)
            return True
        
        else:
            self.current_path = []
            return False
    
    # Dobs use a BFS algorithm to find the best possible path (think: wave)
    def find_path(self, start_pos: tuple[int, int], end_pos: tuple[int, int]) -> list:
        visited = set([start_pos])
        queue = [(start_pos, [])]

        while queue:
            current_pos, path = queue.pop(0)
            if current_pos == end_pos:
                return path

            for neighbor in get_surrounding_tiles(current_pos):
                if neighbor not in visited and tile_available(neighbor):
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return []

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
        self.tiles_in_vision = []

        for x in range(grid_x - sight_distance, grid_x + sight_distance + 1):
            for y in range(grid_y - sight_distance, grid_y + sight_distance + 1):
                if within_bounds((x, y)):
                    self.tiles_in_vision.append((x, y))

        self.memorize_interests(self.tiles_in_vision)

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
        if self.age >= DEATH_AGE:
            self.cause_of_death = "age"

        elif self.current_calories <= 0:
            self.cause_of_death = "starvation"

        elif self.current_hydration <= 0:
            self.cause_of_death = "dehydration"
        
        self.alive = False

    ## Data functions
    # Collects dob's information and returns it
    def collect_package(self) -> dict:
        return {
            "tag": self.tag,
            "cause_of_death": self.cause_of_death
        }
    
    # region HELPER FUNCTIONS

    # Defines all of the dob's starting 'biological' traits
    def generate_biology(self, sex, mom, dad):
        # Brain
        self.brain = Brain()
        self.brain.dob = self
        self.alive = True
        self.age = 0

        self.size = BABY_DOB_SIZE

        self.update_sex_attributes(sex)

        self.mating_cooldown = MATING_COOLDOWN
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

    # Updates the age milestones
    def update_age(self):
        if self.age >= ADULT_AGE:
            self.size = ADULT_DOB_SIZE
        
        elif self.age >= ELDER_AGE:
            pass # for now

        elif self.age >= DEATH_AGE:
            self.die()
            return

    # Updates the sex attributes
    def update_sex_attributes(self, sex):
        self.sex = sex

        if sex == "F":
            self.color = FEMALE_COLOR

        elif sex == "M":
            self.color = MALE_COLOR

    # Checks hunger
    def is_hungry(self) -> bool:
        return self.current_calories < (self.dna["max_calories"] * self.hunger_threshhold)
    
    # Checks thirst
    def is_thirsty(self) -> bool:
        return self.current_hydration < (self.dna["max_hydration"] * self.thirst_threshhold)

    # Checks ability to mate
    def can_mate(self) -> bool:
        return (self.mating_cooldown == 0 and
                self.age >= ADULT_AGE and
                self.current_calories > self.dna["max_calories"] * self.hunger_threshhold and
                self.current_hydration > self.dna["max_hydration"] * self.thirst_threshhold)
    
    # Returns a random tile within vision
    def get_random_tile(self) -> tuple[int, int]:
        return choice(self.tiles_in_vision)
    
    # Memorizes any object in sight to short-term memory
    def memorize_interests(self, coords):
        for coord in coords:
            for obj in GRID_OCCUPANCY.get(coord, []):
                if obj is self:
                    continue
                self.brain.memorize(SHORT_TERM, obj)

    # Increments counters
    def increment(self):
        self.brain.age_memories()

        if self.mating_cooldown > 0:
                self.mating_cooldown -= MATING_COOLDOWN_SPEED

        self.age += AGE_RATE

        if self.age >= ADULT_AGE:
            self.size = TILE_SIZE / 2

    # endregion
