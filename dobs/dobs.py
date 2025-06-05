import pygame
from random import choice
from utilities.config import *
from utilities.utils import tile_occupied, within_bounds, get_adjacent_tiles, remove_object_from_GO
from dobs.brain import Brain
from world_objects import Simulation_Object

class Dob(Simulation_Object):
    _id = 0

    def __init__(self, sex=choice(["F", "M"]), mom=None, dad=None):
        super().__init__()
        self.register(Dob, DOB, ACTIVE_DOBS)
        self.generate_biology(sex, mom, dad)
        self.generate_needs(DEFAULT_MAX_CALORIES, DEFAULT_MAX_HYDRATION, DEFAULT_DOBAMINE)

        self.visited_tiles = [self.grid_pos]
        self.current_path = []

    # Called each tick to handle behavior, cooldowns, aging, and rendering
    def exist(self, surface):
        pygame.draw.circle(surface, self.color, self.pixel_pos, self.size)
        self.see()
        self.brain.think()

        self.increment()

    # region ----- PATHFINDING FUNCTIONS -----

    # Moves dob to grid coords
    def move_towards(self, target: tuple[int, int]) -> bool:
        if len(self.current_path) == 0:
            if self.is_adjacent_to(target):
                return
            self.current_path = self.find_path(self.grid_pos, target)

        if len(self.current_path) == 0:
            return

        next_step = self.current_path[0]

        if not tile_occupied(next_step):
            self.current_dobamine += self.get_tile_dobamine(next_step)
            self.current_path.pop(0)
            self.move_to(next_step)
            self.expend_energy(1)
            return True
        
        else:
            self.current_path = []
            return False
    
    # Dobs use a BFS algorithm to find the best possible path (think: wave)
    def find_path(self, start_pos: tuple[int, int], end_pos: tuple[int, int]) -> list:
        visited = set([start_pos])
        queue = [(start_pos, [])]

        if tile_occupied(end_pos):
            end_pos = find_available_adjacent(self, end_pos)

        while queue:
            current_pos, path = queue.pop(0)
            if current_pos == end_pos:
                return path

            for neighbor in get_adjacent_tiles(current_pos):
                if neighbor not in visited and within_bounds(neighbor):
                    visited.add(neighbor)
                    if not tile_occupied(neighbor) or neighbor == end_pos:
                        queue.append((neighbor, path + [neighbor]))

        return []

    # endregion

    # Defines a variety of actions based on the object (target) being interacted with
    def interact(self, target):
        if target.tag == FOOD:
            self.current_dobamine += 5
            self.current_calories += target.interact_with()
        
        elif target.tag == WATER:
            self.brain.memorize(LONG_TERM, target)
            self.current_dobamine += 5
            self.thirst_threshhold = 0.4
            self.current_hydration += target.interact_with()

        elif target.tag == DOB:
            self.mate(target)
        
        return True
    
    # Calculates all visible tiles within sight distance and then passes visible tiles to memory
    def see(self) -> list:
        grid_x, grid_y = self.grid_pos
        self.tiles_in_vision = []

        for x in range(grid_x - self.sight, grid_x + self.sight + 1):
            for y in range(grid_y - self.sight, grid_y + self.sight + 1):
                if within_bounds((x, y)):
                    self.tiles_in_vision.append((x, y))

        self.memorize_interests(self.tiles_in_vision)
        return self.tiles_in_vision

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
            dob.move_to(female.grid_pos)
            
            female.mating_cooldown = MATING_COOLDOWN
            female.expend_energy(5)
            female.current_dobamine += 5
            female.offspring += 1

            male.mating_cooldown = MATING_COOLDOWN
            male.current_dobamine += 10
            male.expend_energy(3)

            return
        
        self.mating_cooldown += MATING_COOLDOWN/2
    
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

        self.sight = 3
        self.size = BABY_DOB_SIZE

        self.update_sex_attributes(sex)

        self.mating_cooldown = MATING_COOLDOWN
        self.offspring = 0
        self.cause_of_death = ""

    # Defines all of the dob's starting needs
    def generate_needs(self, max_calories, max_hydration, max_dobamine):
        self.max_calories = max_calories
        self.current_calories = max_calories
        self.hunger_threshhold = HUNGER_THRESHHOLD

        self.max_hydration = max_hydration
        self.current_hydration = max_hydration
        self.thirst_threshhold = THIRST_THRESHHOLD

        self.max_dobamine = max_dobamine
        self.current_dobamine = max_dobamine
        self.dobamine_low_threshhold = LOW_DOBAMINE_THRESHHOLD
        self.dobamine_high_threshhold = HIGH_DOBAMINE_THRESHHOLD

    # Updates the age milestones
    def update_age(self):
        if self.age >= DEATH_AGE:
            self.cause_of_death = "age"
            self.die()

        if self.age >= ADULT_AGE:
            self.size = ADULT_DOB_SIZE
        
        elif self.age >= ELDER_AGE:
            pass # for now

    # Updates the sex attributes
    def update_sex_attributes(self, sex):
        self.sex = sex

        if sex == "F":
            self.color = FEMALE_COLOR

        elif sex == "M":
            self.color = MALE_COLOR

    def is_hungry(self) -> bool:
        """Checks hunger"""
        return self.current_calories < (self.max_calories * self.hunger_threshhold)
    
    def is_thirsty(self) -> bool:
        """Checks thirst"""
        return self.current_hydration < (self.max_hydration * self.thirst_threshhold)
    
    def can_mate(self) -> bool:
        """Checks ability to mate"""
        return (self.mating_cooldown == 0 and
                self.age >= ADULT_AGE and
                self.current_calories > self.max_calories * self.hunger_threshhold and
                self.current_hydration > self.max_hydration * self.thirst_threshhold)
    
    def needs_dobamine(self) -> float:
        """Checks dobamine and returns a weight value for the brain"""
        if self.current_dobamine < (self.max_dobamine * self.dobamine_low_threshhold):
            return 0.8
        elif self.current_dobamine < (self.max_dobamine * self.dobamine_high_threshhold):
            return 0.4
        return 0
    
    def get_tile_dobamine(self, coords: tuple[int, int], record_visit: bool=True) -> int:
        """Gets a tile's dobamine exploration reward"""
        if coords not in self.visited_tiles and record_visit:
            self.visited_tiles.append(coords)
        elif coords in self.visited_tiles:
            return -DOBAMINE_EXPLORATION_REWARD
        
        return DOBAMINE_EXPLORATION_REWARD

    def get_tile_in_sight(self, need_dobamine=False) -> tuple[int, int]:
        """Returns a random tile within vision, if need_dobamine = True, only returns positive dobamine tiles"""
        positive_dobamine_tiles = sorted(
            [tile for tile in self.tiles_in_vision if not tile_occupied(tile) and tile not in self.visited_tiles],
            key=lambda t: self.get_grid_distance_to(t)
        )
        neutral_dobamine_tiles = [tile for tile in self.tiles_in_vision if not tile_occupied(tile) and tile in self.visited_tiles]

        if need_dobamine and len(positive_dobamine_tiles) != 0:
            return positive_dobamine_tiles[0]
        
        return choice(positive_dobamine_tiles + neutral_dobamine_tiles)
    
    # Memorizes any object in sight to short-term memory
    def memorize_interests(self, coords):
        for coord in coords:
            for obj in GRID_OCCUPANCY.get(coord, []):
                if obj is self:
                    continue
                if obj.tag == DOB and not obj.can_mate():
                    continue
                self.brain.memorize(SHORT_TERM_MEMORY, obj)

    # Increments counters
    def increment(self):
        self.brain.age_memories()

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
            "hydration": self.current_hydration,
            "age": self.age,
            "dobamine": self.current_dobamine
        }
    
    # endregion

# region ----- LOCAL FUNCTIONS -----

def find_available_adjacent(obj, coords):
        adjacents = get_adjacent_tiles(coords, diagonals=False, avoid_occupied=True)
        while adjacents == []:
            return obj.get_tile_in_sight()
        return choice(adjacents)

# endregion
