from utilities.config import *

class Brain():
    def __init__(self):
        self.dob = None

        self.needs = [
            WATER,
            FOOD,
            REPRODUCTION
        ]

        self.memory = {
            "short": [],
            "long": []
        }
    
    # Function called to determine what a dob is going to do
    def think(self):
        target = self.evaluate()

        if target:
            if self.dob.is_adjacent_to(target):
                self.dob.interact(target)
                return

            self.dob.move_towards(target)
            return

        else:
            self.dob.move_towards()

    # Evaluates what a dob needs most at any given time
    def evaluate(self):
        if self.dob.is_thirsty():
            return self.get_closest_target(WATER)

        elif self.dob.is_hungry():
            return self.get_closest_target(FOOD)

        elif self.dob.can_mate():
            matches = [obj for obj, _ in self.memory[SHORT_TERM] if obj.tag == DOB and obj.sex != self.dob.sex]
            if matches:
                return min(matches, key=lambda m: self.dob.get_grid_distance_to(m))

        return None
    
    # Memorize an object to memory.
    def memorize(self, memory_type, object):
        already_memorized = any(m[0] == object for m in self.memory[memory_type])

        if not already_memorized:
            self.memory[memory_type].append((object, DOB_TRAITS[memory_type]))
    
    ## Helper functions
    # Get the closet target to the dob
    def get_closest_target(self, target):
        matches = self.check_memories(target)
        if matches:
            return min(matches, key=lambda m: self.dob.get_grid_distance_to(m))
        
        return None

    # Checks memories for target, short-term is prioritized
    def check_memories(self, target):
        short = [o for o, _ in self.memory[SHORT_TERM] if o.tag == target]
        long = [o for o, _ in self.memory[LONG_TERM] if o.tag == target]
        
        return short + long

    # Ages memories by 1 per tick, if age == 0, the memory is forgotten
    def age_memories(self):
        for memory_type in self.memory:
            self.memory[memory_type] = [(mem, age - 1) for mem, age in self.memory[memory_type] if age > 1]