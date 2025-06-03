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
            tx, ty = target.get_grid_coordinates()
            dx, dy = self.dob.get_grid_coordinates()

            if abs(tx - dx) + abs(ty - dy) == 1:
                self.dob.interact(target)
                return
            
            self.dob.move_to(target)
            return

        else:
            self.dob.move_to()

    # Evaluates what a dob needs most at any given time
    def evaluate(self):
        if self.dob.is_thirsty():
            return self.get_closest_target(WATER)

        elif self.dob.is_hungry():
            return self.get_closest_target(FOOD)

        elif self.dob.can_mate():
            matches = [obj for obj, _ in self.memory[SHORT_TERM] if obj.object_tag == DOB and obj.sex != self.dob.sex]
            if matches:
                return min(matches, key=lambda m: self.dob.get_grid_distance_between(m.get_grid_coordinates()))

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
            return min(matches, key=lambda m: self.dob.get_grid_distance_between(m.get_grid_coordinates()))
        
        return None

    # Checks memories for target, short-term is prioritized
    def check_memories(self, target):
        short = [o for o, _ in self.memory[SHORT_TERM] if o.object_tag == target]
        long = [o for o, _ in self.memory[LONG_TERM] if o.object_tag == target]
        
        return short + long

    # Ages memories by 1 per tick, if age == 0, the memory is forgotten
    def age_memories(self):
        for memory_type in self.memory:
            self.memory[memory_type] = [(mem, age - 1) for mem, age in self.memory[memory_type] if age > 1]