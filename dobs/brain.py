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
    def think(self) -> bool:
        new_goal = self.determine_goal()
        
        if not self.current_goal or not self.current_goal.get("coords"):
            self.current_goal = new_goal

        coords = self.current_goal.get("coords")
        target = self.current_goal.get("target")
        request = self.current_goal.get("request")

        # If the dob is adjacent to coords (target), interact with it
        if self.dob.is_adjacent_to(coords) and target:
            self.dob.interact(target, request)
            self.current_goal = {}
            return False

        # If the dobs goal has changed, re-evaluate it's path
        if coords != new_goal.get("coords"):
            self.dob.move_towards(new_goal["coords"], repath=True)
            self.current_goal = new_goal
            return False
        
        # If the dobs goals have not changed and it's not adjacent, continue movement
        else:
            self.dob.move_towards(coords)
            return True

    def determine_goal(self):
        """Evaluates what a dob needs most for decision-making"""
        needs = self.get_urgencies()
        most_urgent = max(needs, key=needs.get)

        # Attempts to fulfill the most urgent needs
        if most_urgent == WATER:
            target, coords = self.get_closest_water() # can return (None, None) if no known water
            request = EAT
        elif most_urgent == FOOD:
            target, coords = self.get_closest_food() # can return (None, None) if no known food
            request = EAT
        elif most_urgent == REPRODUCTION:
            target, coords = self.get_closest_mate() # can return (None, None) if no known mates
            request = MATE
        elif most_urgent == POPULATION_DENSITY:
            target, coords = None, self.dob.get_tile_in_sight(AGGRESSIVE_SEARCH)
        elif most_urgent == DOBAMINE() and self.is_partnered():
            partner = self.is_partnered()
            target, coords = partner, partner.grid_pos
            request = COMMUNICATE 

        # If nothing was found, explore based on needs, unless it's a child, then it follows it's mom
        if not coords:
            if self.dob.mom and self.dob.age < ADULT_AGE:
                target, coords = self.dob.mom, self.dob.mom.grid_pos
            else:
                target, coords = self.explore()

        return {
            "target": target,
            "coords": coords,
            "requests": request
        }
    
    def explore(self) -> str:
        """If a dob has no viable target for goals, it will randomly explore based off factors"""
        # Aggressive Search = prioritizes farther tiles with more dobamine gain
        if not self.is_food_secure() or not self.is_water_secure():
            return None, self.dob.get_tile_in_sight(AGGRESSIVE_SEARCH)
        
        # Passive = prioritizes closer tiles regardless of dobamine gain
        elif (self.is_food_secure() and self.is_water_secure()) and random() < self.get_chance_to_wander():
            return None, self.dob.get_tile_in_sight(PASSIVE)
        
        # If no explore mode is valid, return no coords
        return None, None
    def share_memory(self, target):
        # TODO: for memory in memory, get memory value to partner, share
        pass
    
    def get_chance_to_wander(self) -> float:
        """Get a dob's chance to wander, increases with lower dobamine"""
        minimum_cap = 0.2
        dobamine_ratio = 1 - (self.current_dobamine / self.max_dobamine)

        return max(minimum_cap, dobamine_ratio ** 2)

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

                self.add_new_memory(obj, SHORT_TERM_MEMORY)

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
            if mem["memory_type"] != PERMANENT_TERM_MEMORY:
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
        self.send_dobamine_gain()
        mem["memory_type"] = LONG_TERM_MEMORY
        mem["age"] = MEMORY_AGES[LONG_TERM_MEMORY]
        mem["interactions"] = 0

    def add_new_memory(self, obj: object, memory_type: str) -> None:
        """Adds a brand new memory to short-term"""
        self.send_dobamine_gain()

        mem = {
            "object": obj,
            "age": MEMORY_AGES[memory_type],
            "interactions": 0,
            "memory_type": memory_type,
            "tag": obj.tag
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
        """Incrememts dobamine per tick in dob.exist()"""
        dobamine_gain = -5

        if self.is_food_secure():
            dobamine_gain += 1
        
        if self.is_water_secure():
            dobamine_gain += 1
        
        self.send_dobamine_gain(dobamine_gain)

    def send_dobamine_gain(self, gain: int=1) -> None:
        """Increases dobamine by 'gain'"""
        self.current_dobamine = max(0, min(self.max_dobamine, self.current_dobamine + gain))

    # endregion

    # region ----- MATING FUNCTIONS -----

    def determine_sexual_urge(self):
        """Determines a dob's urgency to reproduce"""
        if self.dob.can_mate() and self.is_food_secure() and self.is_water_secure():
            the_urge = (self.hunger_ratio + self.thirst_ratio) / 2

            # If there's a nearby mate, the urge to reproduce is stronger
            nearby_mate = self.get_known_mates()
            if nearby_mate:
                urgency = min(1.0, the_urge + NEARBY_MATE_BONUS)

            else:
                urgency = the_urge
        
        else:
            urgency = 0.0

        return urgency
    
    def get_known_mates(self) -> list:
        """Checks memory for any known mates or returns if there is a partner"""
        for mem in self.memory:
            if mem["tag"] == "partner":
                return [mem["object"]]
            
        return [mem["object"] for mem in self.memory 
                if mem["object"].tag == DOB and
                mem["object"].sex != self.dob.sex and
                mem["object"].can_mate() and
                mem["tag"] != "bad_mate" and
                not mem["object"].brain.is_partnered()]

    def get_closest_mate(self):
        """Gets the closest viable mate to the dob"""
        matches = self.get_known_mates()

        if matches:
            target = min(matches, key=lambda m: self.dob.get_grid_distance_to(m.grid_pos))
            return target, target.grid_pos

        return None, None
    
    def remember_bad_mate(self, bad_mate):
        """Remembers a bad mate so they will not attempt mating again"""
        for mem in self.memory:
            if mem["object"] == bad_mate:
                mem["tag"] = "bad_mate"
                mem["memory_type"] = PERMANENT_TERM_MEMORY
                return
    
    def form_partnership(self, partner):
        for mem in self.memory:
            if mem["object"] == partner:
                mem["tag"] = "partner"
                mem["memory_type"] = PERMANENT_TERM_MEMORY
                return
    
    def is_partnered(self):
        for mem in self.memory:
            if mem["tag"] == "partner":
                return mem["object"]
        return False

    # endregion

    # region ----- GENERAL URGENCY FUNCTIONS -----

    def get_urgencies(self):
        """Determines urgencies for decision making"""
        # Basic ratios of current / max, returns 0.0 to 1.0
        self.thirst_ratio = self.dob.current_hydration / self.dob.max_hydration
        self.hunger_ratio = self.dob.current_calories / self.dob.max_calories

        self.thirst_urgency = 1 - self.thirst_ratio
        self.hunger_urgency = 1 - self.hunger_ratio

        food_security = 0.6 if self.is_food_secure() else 1.0
        water_security = 0.6 if self.is_water_secure() else 1.0

        no_more_offspring = 1.0
        # TODO: Make dobamine selections more modular
        dobamine = 0.0
        if self.is_partnered() and self.has_full_family():
            no_more_offspring = 0.0
            dobamine = 1.0

        return {
            WATER: self.thirst_urgency * water_security,
            FOOD: self.hunger_urgency * food_security,
            REPRODUCTION: self.determine_sexual_urge() * no_more_offspring,
            POPULATION_DENSITY: self.determine_pop_density_urge(),
            DOBAMINE: self.determine_dobamine_needs() * dobamine
        }

    def has_full_family(self):
        return self.dob.offspring == OFFSPRING_LIMIT or self.is_partnered().offspring == OFFSPRING_LIMIT
    
    def determine_pop_density_urge(self):
        """Determines if nearby density above [CROWDING_THRESHHOLD]%, if so, desire to move away grows"""
        visible_dobs = sum(
            1 for coord in self.dob.tiles_in_vision
            if any(obj.tag == DOB for obj in GRID_OCCUPANCY.get(coord, []))
            )
        
        total_tiles = len(self.dob.tiles_in_vision)
        density_ratio = visible_dobs / total_tiles if total_tiles > 0 else 0

        return (density_ratio - CROWDING_THRESHHOLD) * CROWDING_SCALING if density_ratio > CROWDING_THRESHHOLD else 0.0

    def determine_dobamine_needs(self):
        dobamine_ratio = self.current_dobamine / self.max_dobamine
        return min(0.2, 1 - dobamine_ratio)
    
    # endregion

    # region ----- FOOD BRAIN FUNCTIONS -----

    def get_closest_food(self):
        """Get the closet food to the dob"""
        matches = []

        # Checks trees for food, if tree has no food, it may be forgotten
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
        """Checks if dob knows of food or is higher than 60% calories"""
        return len(self.has_memory_of(FOOD, specific_search=LONG_TERM_MEMORY)) > 0 or self.dob.current_calories > self.dob.max_calories * 0.6
    
    # endregion

    # region ----- WATER BRAIN FUNCTIONS -----

    def get_closest_water(self):
        """Get the closet water to the dob"""
        matches = self.has_memory_of(WATER)

        # Since there's only one water object, it's actually checking the closest water tiles
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
        """Checks if dob knows of water or is higher than 60% hydration"""
        return len(self.has_memory_of(WATER, specific_search=LONG_TERM_MEMORY)) > 0 or self.dob.current_hydration > self.dob.max_hydration * 0.6
    
    # endregion
