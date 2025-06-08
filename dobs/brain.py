from utilities.config import *
from utilities.utils import *
from random import random

# TODO: Add aggressive vs passive search modes based on urgency
# TODO: Ponder orb and think how dobamine can affect urgencies
# TODO: Implement weight system (is this where dobamine goes?)
# TODO: Make a communication system so dobs can tell other dobs where food is
# TODO: Make dobs recognize food value and change their eating habits accordingly

# TODO: CLEAN THIS SHIT UP

class Brain():
    def __init__(self):
        self.dob = None

        self.current_goal = {}

        self.max_dobamine = DEFAULT_DOBAMINE
        self.current_dobamine = DEFAULT_DOBAMINE / 2

        ## Memories are in dict format with keys being:
        # object: the specific object in the memory
        # age: the age of the memory, decrements each tick
        # interactions: the number of interactions of a memory
        # type: long-term or short-term
        self.memory = []
    
    # Function called to determine what a dob is going to do
    def think(self):
        goal = self.determine_goal()
        
        if not self.current_goal or not self.current_goal.get("coords"):
            self.current_goal = goal

        coords = self.current_goal.get("coords")
        target = self.current_goal.get("target")

        # If the dob is adjacent to coords (target), interact with it
        if self.dob.is_adjacent_to(coords) and target:
            self.dob.interact(target)
            self.current_goal = {}
            return

        # If the dobs goal has changed, re-evaluate it's path
        if self.current_goal != goal:
            self.dob.move_towards(goal["coords"], repath=True)
            self.current_goal = goal
        
        # If the dobs goals have not changed and it's not adjacent, continue movement
        else:
            self.dob.move_towards(coords)

    # Evaluates what a dob needs most at any given time
    def determine_goal(self):
        needs = self.get_urgencies()
        most_urgent = max(needs, key=needs.get)
    
        if most_urgent == WATER:
            target, coords = self.get_closest_water()

        elif most_urgent == FOOD:
            target, coords = self.get_closest_food()

        elif most_urgent == REPRODUCTION:
            target, coords = self.get_closest_mate()

        elif most_urgent == POPULATION_DENSITY:
            print(f"Dob ({self.dob.id}) wants to get the F away from these people!")
            target, coords = None, self.dob.get_tile_in_sight(AGGRESSIVE)

        if not target and (self.dob.mom and self.dob.age < ADULT_AGE):
            target, coords = self.dob.mom, self.dob.mom.grid_pos

        if not target and not coords:
            exploration_mode = self.get_exploration_mode()
            wander_chance = max(0.2, 1.0 * (1 - (self.current_dobamine / self.max_dobamine))**2)
            
            if (exploration_mode == PASSIVE and random() < wander_chance) or exploration_mode == AGGRESSIVE:
                target, coords = None, self.dob.get_tile_in_sight(exploration_mode)
            
            else:
                target, coords = None, None
                
        return {
            "target": target,
            "coords": coords
        }
    
    # region ----- MEMORY FUNCTIONS -----

    def attempt_to_memorize(self, coords: list) -> None:
        """Determines if a coord is worth memorizing or reinforcing"""
        for coord in coords:
            for obj in GRID_OCCUPANCY.get(coord, []):
                # Ignores memorizing itself and dobs who are not potential mates
                if obj is self:
                    continue
                # Changes food to their respective tree for memorization
                if obj.tag == FOOD and obj.tree != None:
                    obj = obj.tree
                # Reinforces a memory a bit, if they've seen it before
                if self.does_memory_exist(obj):
                    self.reinforce_memory(obj, reinforcement=5)
                    continue

                self.add_new_memory(obj)

    def reinforce_memory(self, target: object, reinforcement: int=0, interact: bool=False) -> None:
        """Reinforces a memory by 'reinforcement' and increases interactions"""
        if target.tag == FOOD and target.tree != None:
            target = target.tree

        for mem in self.memory:
            if mem["object"] == target:
                # Updates the age by the reinforcement parameter
                mem["age"] = min((mem["age"] + reinforcement), MEMORY_AGES[mem["memory_type"]])

                # If interact is being called, adds an interaction
                if interact:
                    mem["interactions"] += 1

                # If interacted with enough, promotes memory by setting to long-term memory age, otherwise, just reinforces
                if mem["interactions"] >= INTERACTIONS_TO_PROMOTE and mem["memory_type"] == SHORT_TERM_MEMORY:
                    self.promote_memory(mem)

    def age_memories(self) -> None:
        """Ages memories by 1 per tick, if age == 0, the memory is forgotten"""
        updated_memories = []

        for mem in self.memory:
            mem["age"] -= 1

            if mem["age"] < 0:
                chance_to_forget = min(1.0, abs(mem["age"]) * FORGET_CHANCE_PER) 
                if random() < chance_to_forget:
                    continue

            updated_memories.append(mem)

        self.memory = updated_memories

    # -- MEMORY HELPER FUNCTIONS --

    def promote_memory(self, mem: dict) -> None:
        """Promotes a memory to long-term"""
        self.send_dobamine_gain(2)
        mem["memory_type"] = LONG_TERM_MEMORY
        mem["age"] = MEMORY_AGES[LONG_TERM_MEMORY]
        mem["interactions"] = 0

    def add_new_memory(self, obj: object) -> None:
        """Adds a brand new memory to short-term"""
        self.send_dobamine_gain(1)
        mem = {
            "object": obj,
            "age": MEMORY_AGES[SHORT_TERM_MEMORY],
            "interactions": 0,
            "memory_type": SHORT_TERM_MEMORY
        }
            
        self.memory.append(mem)

    def does_memory_exist(self, obj: object) -> bool:
        """Checks memory for an object"""
        return any(mem["object"] == obj for mem in self.memory)
    
    def get_memory(self, obj: object) -> tuple[dict, str]:
        """Gets a memory and returns it's dict and memory type"""
        for mem in self.memory:
            if mem["object"] == obj:
                return mem, mem["memory_type"]
        
        return None, None
    
    def forget_memory(self, obj: object) -> None:
        """Forgets a memory if the interactions get too low"""
        mem, _ = self.get_memory(obj)
        
        mem["interactions"] -= 1

        if mem["interactions"] < 0:
            print(f"Dob ({self.dob.id}) forgot a memory: {mem["object"].tag}, {mem["object"].grid_pos}!")
            self.memory.remove(mem)

    def has_memory_of(self, tag: str, specific_search: str=None) -> list:
        """Checks memories for tags, returns list prioritizing short-term first"""
        short = [mem["object"] for mem in self.memory if mem["memory_type"] == SHORT_TERM_MEMORY and mem["object"].tag == tag]
        if specific_search == SHORT_TERM_MEMORY:
            return short
        
        long = [mem["object"] for mem in self.memory if mem["memory_type"] == LONG_TERM_MEMORY and mem["object"].tag == tag]
        if specific_search == LONG_TERM_MEMORY:
            return long
        
        return short + long
    
    # endregion
    
    # region ----- DOBAMINE FUNCTIONS -----

    def get_dobamine_gain(self) -> int:
        dobamine_gain = -5

        if self.is_food_secure():
            dobamine_gain += 1
        
        if self.is_water_secure():
            dobamine_gain += 1
        
        self.send_dobamine_gain(dobamine_gain)

    def send_dobamine_gain(self, gain: int) -> None:
        self.current_dobamine = max(0, min(self.max_dobamine, self.current_dobamine + gain))

    # endregion

    # region ----- MATING FUNCTIONS -----

        # Determines a dobs urgency
    def determine_sexual_urge(self):
        if self.dob.can_mate() and self.is_food_secure() and self.is_water_secure():
            the_urge = (self.hunger_ratio + self.thirst_ratio) / 2

            nearby_mate = self.get_known_mates()

            if nearby_mate:
                urgency = min(1.0, the_urge + 0.3)
            
            else:
                urgency = the_urge
        
        else:
            urgency = 0.0

        return urgency
    
    def determine_pop_density_urge(self):
        density = sum(
            1 for coord in self.dob.tiles_in_vision
            if any(obj.tag == DOB for obj in GRID_OCCUPANCY.get(coord, []))
            )
        
        total_tiles = len(self.dob.tiles_in_vision)
        density_ratio = density / total_tiles if total_tiles > 0 else 0

        return (density_ratio - 0.4) * 2 if density_ratio > 0.4 else 0.0
    
    # Locates any known mates
    def get_known_mates(self):
        return [mem["object"] for mem in self.memory 
                if mem["object"].tag == DOB and
                mem["object"].sex != self.dob.sex and
                mem["object"].can_mate()]

    # Get the closet opposite sex dob to the dob
    def get_closest_mate(self):
        matches = self.get_known_mates()

        if matches:
            target = min(matches, key=lambda m: self.dob.get_grid_distance_to(m.grid_pos))
            return target, target.grid_pos

        return None, None
    
    # endregion

    # region ----- HELPER FUNCTIONS -----

    # Determines urgencies for decision making
    def get_urgencies(self):
        self.thirst_ratio = self.dob.current_hydration / self.dob.max_hydration
        self.hunger_ratio = self.dob.current_calories / self.dob.max_calories

        self.thirst_urgency = 1 - self.thirst_ratio
        self.hunger_urgency = 1 - self.hunger_ratio

        food_security = 0.8 if self.is_food_secure() else 1.0
        water_security = 0.8 if self.is_water_secure() else 1.0

        return {
            WATER: self.thirst_urgency * water_security,
            FOOD: self.hunger_urgency * food_security,
            REPRODUCTION: self.determine_sexual_urge(),
            POPULATION_DENSITY: self.determine_pop_density_urge()
        }

    def get_exploration_mode(self) -> str:
        low_calories = self.dob.current_calories < self.dob.max_calories * DANGER_THRESHHOLD
        low_hydration = self.dob.current_hydration < self.dob.max_hydration * DANGER_THRESHHOLD

        if (low_calories and not self.is_food_secure()) or (low_hydration and not self.is_water_secure()):
            return AGGRESSIVE
        
        return PASSIVE

    # Get the closet food to the dob
    def get_closest_food(self):
        matches = []

        for tree in self.has_memory_of(TREE):
            if not tree.grown_foods:
                self.forget_memory(tree)
                continue
            matches.extend(tree.grown_foods)

        if matches:
            target = min(matches, key=lambda m: self.dob.get_grid_distance_to(m.grid_pos))
            return target, target.grid_pos

        return None, None

    def is_food_secure(self) -> bool:
        return len(self.has_memory_of(FOOD, specific_search=LONG_TERM_MEMORY)) > 0 or self.dob.current_calories > self.dob.max_calories * 0.6
    
    # Get the closet water to the dob
    def get_closest_water(self):
        matches = self.has_memory_of(WATER)

        closest = None, None
        closest_dist = float('inf')
        
        for target in matches:
            for tile in target.water_positions:
                dist = self.dob.get_grid_distance_to(tile)
                if dist < closest_dist:
                    closest_dist = dist
                    closest = target, tile

        return closest

    def is_water_secure(self) -> bool:
        return len(self.has_memory_of(WATER, specific_search=LONG_TERM_MEMORY)) > 0 or self.dob.current_hydration > self.dob.max_hydration * 0.6
    
    # endregion
