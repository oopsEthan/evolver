import pygame
from random import choice, choices, randint, random
from utilities.config import *
from utilities.utils import *
from dobs.brain import Brain
from world_objects import Simulation_Object

class Dob(Simulation_Object):
    _id = 0

    def __init__(self, sex=None, mom=None, dad=None):
        super().__init__()
        self.register(Dob, DOB, db=ACTIVE_DOBS)
        self.generate_biology(sex, mom, dad)
        self.generate_needs()

        self.visited_tiles = [self.grid_pos]
        self.current_path = []

    # Called each tick to handle behavior, cooldowns, aging, and rendering
    def exist(self, surface, tick):
        pygame.draw.circle(surface, self.color, self.pixel_pos, self.size)

        self.see()
        goal_change_DEBUG = self.brain.think()

        self.increment(tick)

    # region ----- PATHFINDING FUNCTIONS -----

    # Moves dob to grid coords
    def move_towards(self, target: tuple[int, int], repath: bool=False) -> bool:
        if len(self.current_path) == 0 or repath:
            self.current_path = self.find_path(self.grid_pos, target)

        if len(self.current_path) == 0:
            print(f"ERROR: Dob ({self.id}) path returned as {self.current_path}")
            return

        next_step = self.current_path[0]

        if not tile_occupied(next_step):
            self.current_path.pop(0)
            self.move_to(next_step)
            self.expend_energy(calories=1, hydration=1)
            return True
        
        else:
            # TODO: Instead of just clearing the path, do a quick check if there's a new path to the end_pos, if not, cancel path
            self.current_path = self.find_path(self.grid_pos, target, quick_repath=True)
            return False
    
    # Dobs use a BFS algorithm to find the best possible path (think: wave)
    def find_path(self, start_pos: tuple[int, int], end_pos: tuple[int, int], quick_repath: bool=False) -> list:
        visited = set([start_pos])
        queue = [(start_pos, [])]

        if tile_occupied(end_pos):
            if quick_repath:
                print("quick repath, sending []")
                return []
            end_pos = choice(get_available_adjacents(end_pos))
            if not end_pos:
                print("no end pos, sending []")
                return []

        while queue:
            current_pos, path = queue.pop(0)
            if current_pos == end_pos:
                return path

            for neighbor in get_available_adjacents(current_pos):
                if neighbor not in visited and within_bounds(neighbor):
                    visited.add(neighbor)
                    if not tile_occupied(neighbor) or neighbor == end_pos:
                        queue.append((neighbor, path + [neighbor]))

        print(f"no path found from {start_pos} to {end_pos}!")
        return []

    # endregion

    # Defines a variety of actions based on the object (target) being interacted with
    def interact(self, target: object, request: str) -> None:
        if target.tag != DOB and request == EAT:
            if target.tag == FOOD:
                self.current_calories += target.energy_value

            elif target.tag == WATER:
                self.current_hydration += target.energy_value
            
            self.brain.send_dobamine_gain(5)
            self.brain.current_goal = {}

        elif target.tag == DOB and request == MATE:
            if self.sex == MALE and self.can_mate():
                self.attempt_to_mate(target)
        
        # elif target.tag == DOB and request == COMMUNICATE:
        #     self.share_memory(target)
        #     # TODO: create share_memory

        # if self.brain.does_memory_exist(target):
        #         self.brain.reinforce_memory(target, reinforcement=5, interact=True)
    
    # Calculates all visible tiles within sight distance and then passes visible tiles to memory
    def see(self) -> list:
        grid_x, grid_y = self.grid_pos
        tiles_in_vision = []

        for x in range(grid_x - self.sight, grid_x + self.sight + 1):
            for y in range(grid_y - self.sight, grid_y + self.sight + 1):
                if within_bounds((x, y)):
                    tiles_in_vision.append((x, y))

        self.brain.receive_tiles_in_sight(tiles_in_vision)

    # When dobs do something that requires energy, this is called to expend it
    def expend_energy(self, calories, hydration):
            self.current_calories -= (calories * FOOD_MULTIPLIER) if self.age >= ADULT_AGE else (calories * (FOOD_MULTIPLIER * 0.5))
            self.current_hydration -=  (hydration * WATER_MULTIPLIER) if self.age >= ADULT_AGE else (calories * (WATER_MULTIPLIER * 0.5))

            if self.current_calories <= 0 or self.current_hydration <= 0:
                self.die()
    
    # Mating creates a new dob with a combo of mom and dad's stats
    # Mating is only possible if both dobs are mating age and not on cooldown
    def attempt_to_mate(self, female):
        if not self.determine_viable_mate(female):
            self.brain.remember_bad_mate(female)
            female.brain.remember_bad_mate(self)
            return

        if female.can_mate() and (female.determine_viable_mate(self) or 
                                  female.brain.is_partnered() == self):
            
            dob = Dob(mom=female, dad=self)
            dob.move_to(female.grid_pos)
            
            female.mating_cooldown = MATING_COOLDOWN
            female.expend_energy(calories=50, hydration=2) # * FOOD_COST and * WATER_COST
            female.brain.send_dobamine_gain(10)
            female.offspring += 1

            self.mating_cooldown = MATING_COOLDOWN
            self.brain.send_dobamine_gain(10)
            self.expend_energy(calories=50, hydration=3)

            self.brain.form_partnership(female)
            female.brain.form_partnership(self)

            self.brain.current_goal = {}
            return
        
        elif not female.determine_viable_mate(self):
            female.brain.remember_bad_mate(self)
            self.brain.remember_bad_mate(female)
            self.brain.current_goal = {}
            return

        else:
            self.brain.current_goal = {}
            female.mating_cooldown += MATING_COOLDOWN/2
            self.mating_cooldown += MATING_COOLDOWN/2
    
    # Only females should call this
    def determine_viable_mate(self, potential_mate: object):
        chance_to_mate = 0.0

        if potential_mate.death_age >= self.death_age:
            chance_to_mate += 0.35
        
        if potential_mate.max_calories >= self.max_calories:
            chance_to_mate += 0.35
        
        if potential_mate.max_hydration >= self.max_hydration:
            chance_to_mate += 0.35

        result = random() < chance_to_mate + 0.05

        # print(f"[Mate Check] F:{self.id} M:{male.id} → chance: {chance_to_mate:.2f} → {'✔' if result else '✖'}")

        return result
    
    # Defines a dob's cause of death and sets them to dead - RIP
    def die(self):
        if self.current_calories <= 0:
            self.cause_of_death = "starvation"

        elif self.current_hydration <= 0:
            self.cause_of_death = "dehydration"
        
        remove_object_from_GO(self)
        self.alive = False

        print(f"Dob #{self.id} died of {self.cause_of_death} at age {self.age}.")

    # region ----- HELPER FUNCTIONS -----

    # Defines all of the dob's starting 'biological' traits
    def generate_biology(self, sex, mom, dad):
        # Brain
        self.brain = Brain()
        self.brain.dob = self
        self.alive = True

        self.age = 0

        self.mom = mom
        self.dad = dad
        self.generate_dna(mom, dad)

        self.sight = 3
        self.size = BABY_DOB_SIZE

        if sex == None:
            sex = choice([FEMALE, MALE])

        self.update_sex_attributes(sex)

        self.mating_cooldown = MATING_COOLDOWN
        self.offspring = 0
        self.cause_of_death = ""

    def generate_dna(self, mom=None, dad=None):
        if mom and dad:
            self.death_age = int((mom.death_age + dad.death_age) / 2) + randint(*DEATH_AGE_MOD)
            self.max_calories = int((mom.max_calories + dad.max_calories) / 2) + randint(*DEFAULT_CALORIES_MOD)
            self.max_hydration = int((mom.max_hydration + dad.max_hydration) / 2) + randint(*DEFAULT_WATER_MOD)
        
        else:
            self.death_age = DEFAULT_DEATH_AGE + randint(*DEATH_AGE_MOD)
            self.max_calories = DEFAULT_MAX_CALORIES + randint(*DEFAULT_CALORIES_MOD)
            self.max_hydration = DEFAULT_MAX_HYDRATION + randint(*DEFAULT_WATER_MOD)
        
        self.elder_age = self.calculate_elder_age()
    
    def calculate_elder_age(self) -> int:
        return self.death_age - TICKS_DOBS_LIVE_AT_ELDER_AGE
    
    # Defines all of the dob's starting needs
    def generate_needs(self):
        self.current_calories = self.max_calories
        self.hunger_threshhold = HUNGER_THRESHHOLD

        self.current_hydration = self.max_hydration
        self.thirst_threshhold = THIRST_THRESHHOLD

    # Updates the age milestones
    def update_age(self):
        if self.age >= self.death_age:
            self.cause_of_death = "age"
            self.die()

        if self.age >= ADULT_AGE:
            self.size = ADULT_DOB_SIZE
        
        elif self.age >= self.elder_age:
            self.sight -= 1

    # Updates the sex attributes
    def update_sex_attributes(self, sex):
        self.sex = sex

        if sex == FEMALE:
            self.color = FEMALE_COLOR

        elif sex == MALE:
            self.color = MALE_COLOR
        
        mutation = (
            max(0, self.color[0] + randint(*COLOR_VARIATION)),
            max(0, self.color[1] + randint(*COLOR_VARIATION)),
            self.color[2]
        )

        self.color = mutation
    
    def can_mate(self) -> bool:
        """Checks ability to mate"""
        if self.sex == MALE:
            return self.mating_cooldown == 0 and self.is_viable_mating_age()
        elif self.sex == FEMALE:
            return (self.mating_cooldown == 0 and
                    self.is_viable_mating_age() and
                    self.offspring < OFFSPRING_LIMIT)
                    
    def is_viable_mating_age(self) -> bool:
        return self.elder_age >= self.age >= ADULT_AGE
    
    # Increments counters
    def increment(self, tick):
        self.brain.age_memories()

        if tick % 5 == 0: # every 5 ticks
            self.expend_energy(calories=5, hydration=1)
            self.brain.get_dobamine_decay()

        if self.mating_cooldown > 0:
                self.mating_cooldown -= MATING_COOLDOWN_SPEED


        self.age += AGE_RATE
        self.update_age()

    # endregion

    # region ----- DATA FUNCTIONS -----

    # Collects dob's information and returns it
    def collect_package(self) -> dict:
        return {
            "tag": self.tag,
            "cause_of_death": self.cause_of_death
        }
    
    def collect_stats(self) -> dict:
        return {
            "calories": self.current_calories,
            "max_calories": self.max_calories,
            "hydration": self.current_hydration,
            "max_hydration": self.max_hydration,
            "age": self.age,
            "death_age": self.death_age,
            "dobamine": self.brain.current_dobamine,
            "water_security": self.brain.is_water_secure(),
            "food_security": self.brain.is_food_secure()
        }
    
    # endregion