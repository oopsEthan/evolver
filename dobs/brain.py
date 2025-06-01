from config import *

class Brain():
    def __init__(self):
        self.dob = None

        self.needs = [
            WATER,
            FOOD
            # "reproduction"
        ]

        self.short_term_memory = []
        self.long_term_memory = []

    def think(self):
        target = self.evaluate()

        if target:
            tx, ty = target["grid_loc"]
            dx, dy = self.dob.get_grid_coordinates()

            if abs(tx - dx) + abs(ty - dy) == 1:
                self.dob.interact(target["object"])
                return
            
            self.dob.move_to(target)

        elif not target:
            self.dob.move_to()

    def memorize(self, dob, target_memory, memory):
        already_seen = any(m["object"] == memory["object"] for m in self.short_term_memory)

        if target_memory == "short" and not already_seen:
            memory["age"] = DOB_TRAITS["SHORT_TERM_AGE"]
            self.short_term_memory.append(memory)
        
            print(f"Dob #{dob.id} memorized {memory['object'].get_grid_coordinates()}!")

    def forget(self):
        for memory in self.short_term_memory:
            memory["age"] -= 1
        
        self.short_term_memory = [memory for memory in self.short_term_memory if memory["age"] > 0]

    def evaluate(self):
        for need in self.needs:
            if self.dob.check(need):
                matches = [m for m in self.short_term_memory if m["object"].object_tag == need]
                if matches:
                    target = min(matches, key=lambda m: self.dob.get_grid_distance_between(m["grid_loc"]))
                    return target
        
        return None