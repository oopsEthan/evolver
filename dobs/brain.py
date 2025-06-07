from utilities.config import *
from utilities.utils import *
from random import random

# TODO: Add aggressive vs passive search modes based on urgency
# TODO: Ponder orb and think how dobamine can affect urgencies
# TODO: Implement weight system (is this where dobamine goes?)
# TODO: Make a communication system so dobs can tell other dobs where food is
# TODO: Make dobs recognize food value and change their eating habits accordingly
# TODO: Make dobs memory not decay in such a sudden manner, add reinforcement

class Brain():
    def __init__(self):
        self.dob = None

        self.current_goal = {}

        self.memory = {
            SHORT_TERM_MEMORY: [],
            LONG_TERM_MEMORY: []
        }
    
    # Function called to determine what a dob is going to do
    def think(self):
        goal = self.determine_goal()
        
        if not self.current_goal:
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
        
        if not target or not coords:
            exploration_weight = self.dob.needs_dobamine()

            if random() < exploration_weight:
                target, coords = None, self.dob.get_tile_in_sight(need_dobamine=True)
            
            else:
                target, coords = None, self.dob.get_tile_in_sight()

        return {
            "target": target,
            "coords": coords
        }
    
    # Memorize an object to memory.
    def update_memories(self, memory_type, object):
        already_memorized = any(m[0] == object for m in self.memory[memory_type])
        
        new_memory = []
        for m in self.memory[memory_type]:
            obj_ref = m[0]
            if obj_ref == object and not check_GO(obj_ref.grid_pos):
                print(f"[Memory Cleanup] Forgetting {obj_ref.tag} #{getattr(obj_ref, 'id', '?')} — no longer at {obj_ref.grid_pos}")
                continue
            new_memory.append(m)

        self.memory[memory_type] = new_memory

        if not already_memorized:
            self.memory[memory_type].append((object, MEMORY_AGES[memory_type]))
    
    # region ----- HELPER FUNCTIONS -----

    # Determines urgencies for decision making
    def get_urgencies(self):
        self.thirst_ratio = self.dob.current_hydration / self.dob.max_hydration
        self.hunger_ratio = self.dob.current_calories / self.dob.max_calories

        self.thirst_urgency = 1 - self.thirst_ratio
        self.hunger_urgency = 1 - self.hunger_ratio

        return {
            WATER: self.thirst_urgency,
            FOOD: self.hunger_urgency,
            REPRODUCTION: self.determine_sexual_urge()
        }

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
    def get_closest_mate(self):
        matches = self.get_known_mates()
        if matches:
            target = min(matches, key=lambda m: self.dob.get_grid_distance_to(m.grid_pos))
            return target, target.grid_pos

        return None, None
    
    # Determines a dobs urgency
    def determine_sexual_urge(self):
        if self.dob.can_mate():
            the_urge = (self.hunger_ratio + self.thirst_ratio) / 2

            nearby_mate = self.get_known_mates()

            if nearby_mate:
                urgency = min(1.0, the_urge + 0.3)
            
            else:
                urgency = the_urge
        
        else:
            urgency = 0.0

        return urgency
    
    def get_known_mates(self):
        return [obj for obj, _ in self.memory[SHORT_TERM_MEMORY] if obj.tag == DOB and obj.sex != self.dob.sex]

    # Checks memories for target, short-term is prioritized
    def check_memories(self, target):
        short = [o for o, _ in self.memory[SHORT_TERM_MEMORY] if o.tag == target]
        long = [o for o, _ in self.memory[LONG_TERM_MEMORY] if o.tag == target]
        
        return short + long

    # TODO: Make this less flat and more dynamic!
    # Ages memories by 1 per tick, if age == 0, the memory is forgotten
    def age_memories(self):
        for memory_type in self.memory:
            updated_memories = []

            for mem, age in self.memory[memory_type]:
                age -= 1

                if age < 0:
                    chance_to_forget = min(1.0, abs(age) * FORGET_CHANCE_PER)  
                    if random() < chance_to_forget:
                        print(f"A dob forgot {mem}, lol!")
                        continue
                updated_memories.append((mem, age))

            self.memory[memory_type] = updated_memories

            # self.memory[memory_type] = [(mem, age - 1) for mem, age in self.memory[memory_type] if age > 1]

    # endregion
