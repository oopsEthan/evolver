from config import *

class Brain():
    def __init__(self):
        self.dob = None

        self.needs = [
            REPRODUCTION,
            WATER,
            FOOD
        ]

        self.short_term_memory = []
        self.long_term_memory = []

    def think(self):
        target = self.evaluate()

        if target:
            tx, ty = target.get_grid_coordinates()
            dx, dy = self.dob.get_grid_coordinates()

            if abs(tx - dx) + abs(ty - dy) == 1:
                self.dob.interact(target)
                return
            
            self.dob.move_to(target)

        else:
            self.dob.move_to()

    def memorize(self, target_memory, obj):
        if target_memory == "short":
            already_seen = any(m[0] == obj for m in self.short_term_memory)
            if not already_seen:
                self.short_term_memory.append((obj, DOB_TRAITS["SHORT_TERM_AGE"]))

        elif target_memory == "long":
            if obj not in self.long_term_memory:
                print(f"Dob #{self.dob.id} memorized an object's location: '{obj.object_tag}'={obj.get_grid_coordinates()}")
                self.long_term_memory.append(obj)

    def forget(self):
        updated_memory = []
        for obj, age in self.short_term_memory:
            if age > 1:
                updated_memory.append((obj, age - 1))
        self.short_term_memory = updated_memory

    def evaluate(self):
        target = None

        for need in self.needs:
            if self.dob.check(need) and (need == FOOD or need == WATER):
                matches = self.remember("short", need) + self.remember("long", need)
                if matches:
                    target = min(matches, key=lambda m: self.dob.get_grid_distance_between(m.get_grid_coordinates()))

            elif (self.dob.check(need) and
                  need == REPRODUCTION and
                  self.dob.sex_drive >= 30):
                matches = [obj for obj, _ in self.short_term_memory
                           if obj.object_tag == "dob" and obj.sex != self.dob.sex]
                if matches:
                    target = min(matches, key=lambda m: self.dob.get_grid_distance_between(m.get_grid_coordinates()))

            if target:
                print(f"Dob #{self.dob.id} is targeting '{target.object_tag}'!")
                return target

        return None

    def remember(self, target_memory, need_tag):
        if target_memory == "short":
            return [obj for obj, _ in self.short_term_memory if obj.object_tag == need_tag]
        
        elif target_memory == "long":
            return [obj for obj in self.long_term_memory if obj.object_tag == need_tag]