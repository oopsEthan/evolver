from utilities.config import *
from random import random

class Brain():
    def __init__(self):
        self.dob = None

        self.needs = [
            WATER,
            FOOD,
            DOBAMINE,
            REPRODUCTION
        ]

        self.memory = {
            SHORT_TERM_MEMORY: [],
            LONG_TERM_MEMORY: []
        }
    
    # Function called to determine what a dob is going to do
    def think(self):
        target, coords = self.evaluate()

        if coords is None:
            print(f"Dob #{self.dob.id} has no coords to move to.")
            return

        if self.dob.is_adjacent_to(coords) and target:
            self.dob.interact(target)
            return

        self.dob.move_towards(coords)
        return

        # else:
        #     if random() > 0.5:
        #         self.dob.move_towards(self.dob.get_tile_in_sight())
        #     return

    # Evaluates what a dob needs most at any given time
    def evaluate(self):
        target, coords = None, None

        if self.dob.is_thirsty():
            target, coords = self.get_closest_water()

        elif self.dob.is_hungry():
            target, coords = self.get_closest_food()

        elif self.dob.can_mate():
            target, coords = self.get_closest_dob()
        
        if not target or not coords:
            exploration_weight = self.dob.needs_dobamine()

            if random() < exploration_weight:
                target, coords = None, self.dob.get_tile_in_sight(need_dobamine=True)
            
            else:
                target, coords = None, self.dob.get_tile_in_sight()

        return target, coords
    
    # Memorize an object to memory.
    def memorize(self, memory_type, object):
        already_memorized = any(m[0] == object for m in self.memory[memory_type])

        if not already_memorized:
            self.memory[memory_type].append((object, MEMORY_AGES[memory_type]))
    
    # region ----- HELPER FUNCTIONS -----

    # Get the closet food to the dob
    def get_closest_food(self):
        matches = self.check_memories(FOOD)
        if matches:
            target = min(matches, key=lambda m: self.dob.get_grid_distance_to(m.grid_pos))
            return target, target.grid_pos

        return None, None

    # Get the closet water to the dob
    def get_closest_water(self):
        matches = self.check_memories(WATER)

        closest = None, None
        closest_dist = float('inf')
        
        for target in matches:
            for tile in target.water_positions:
                dist = self.dob.get_grid_distance_to(tile)
                if dist < closest_dist:
                    closest_dist = dist
                    closest = target, tile

        return closest

    # Get the closet opposite sex dob to the dob
    def get_closest_dob(self):
        matches = [obj for obj, _ in self.memory[SHORT_TERM_MEMORY] if obj.tag == DOB and obj.sex != self.dob.sex]
        if matches:
            target = min(matches, key=lambda m: self.dob.get_grid_distance_to(m.grid_pos))
            return target, target.grid_pos


        return None, None

    # Checks memories for target, short-term is prioritized
    def check_memories(self, target):
        short = [o for o, _ in self.memory[SHORT_TERM_MEMORY] if o.tag == target]
        long = [o for o, _ in self.memory[LONG_TERM_MEMORY] if o.tag == target]
        
        return short + long

    # Ages memories by 1 per tick, if age == 0, the memory is forgotten
    def age_memories(self):
        for memory_type in self.memory:
            self.memory[memory_type] = [(mem, age - 1) for mem, age in self.memory[memory_type] if age > 1]

    # endregion
