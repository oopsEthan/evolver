import pygame
from random import randrange
from config import MAX_X, MAX_Y, CELL_SIZE, ACTIVE_FOOD, ACTIVE_WATER, DOB_TRAITS
from world_objects import Simulation_Object

SHORT = "short"
LONG = "long"

class Dob(Simulation_Object):
    _id = 0

    def __init__(self):
        super().__init__()
        self.id = Dob._id
        Dob._id += 1

        self.brain = Brain()
        self.alive = True

        self.dna = {
            "sight": 2,
            "max_calories": 1000,
            "max_hydration": 50,
        }

        self.current_calories = self.dna["max_calories"] * 0.8
        self.current_hydration = self.dna["max_hydration"]

        self.spawn()

    # Movement
    def wander(self):
        moved = False

        while not moved:
            x_change = randrange(-1, 2) * CELL_SIZE
            y_change = randrange(-1, 2) * CELL_SIZE

            new_position = self.current_location + pygame.Vector2(x_change, y_change)

            moved = self.move(new_position)

    def pursue(self):
        known_need = [mem for mem in self.brain.short_term_memory["visible"] if mem["type"] == "need"]

        if not known_need:
            return False
        
        target = min(
            known_need,
            key=lambda m: self.get_grid_distance_between(m["grid_loc"])
        )

        fx, fy = target["grid_loc"]
        dx, dy = self.get_grid_coordinates()
        
        if abs(fx - dx) <= 1 and abs(fy - dy) <= 1:
            self.consume(target)
            
        move_x = fx - dx
        move_y = fy - dy

        if abs(move_x) > abs(move_y):
            step = pygame.Vector2(CELL_SIZE if move_x > 0 else -CELL_SIZE, 0)
        else:
            step = pygame.Vector2(0, CELL_SIZE if move_y > 0 else -CELL_SIZE)
        
        new_position = self.current_location + step
        self.move(new_position)

    def consume(self, target):
            self.brain.short_term_memory["visible"].remove(target)
            energy_input, energy_category = target["object"].absorb()

            if energy_category == "food":
                self.current_calories += energy_input
                print(f"Dob #{self.id} gained {energy_input} calories, bringing them to {self.current_calories} calories!")
            
            if energy_category == "water":
                self.current_hydration += energy_input
                print(f"Dob #{self.id} gained {energy_input} hydration, bringing them to {self.current_hydration} hydration!")

            return True
    
    def see(self):
        grid_x = int(self.current_location.x // CELL_SIZE)
        grid_y = int(self.current_location.y // CELL_SIZE)
        sight_distance = self.dna["sight"]

        interests = [
            ("need", ACTIVE_FOOD),
            ("need", ACTIVE_WATER)
        ]

        visible_tiles = []

        for x in range(grid_x - sight_distance, grid_x + sight_distance + 1):
            for y in range(grid_y - sight_distance, grid_y + sight_distance + 1):
                if 0 <= x < MAX_X // CELL_SIZE and 0 <= y < MAX_Y // CELL_SIZE:
                    visible_tiles.append((x, y))

        for interest_type, interest_object in interests:
            for object in interest_object:
                if object.get_grid_coordinates() in visible_tiles:
                    memory = {
                        "type": interest_type,
                        "need_type": object.caloric_category,
                        "object": object,
                        "grid_loc": object.get_grid_coordinates()
                    }
                        
                    self.brain.memorize(self, SHORT, memory)
                    print(f"Dob #{self.id} spotted a '{interest_type}' at {object.get_grid_coordinates()}!")

        return visible_tiles

    def expend_energy(self, factor):
        self.current_calories -= 10 * factor
        self.current_hydration -= 1 * factor

        if self.current_calories == 0 or self.current_hydration == 0:
            # self.alive = False
            pass
        
    def exist(self, surface):
        pygame.draw.circle(surface, "blue", self.current_location, CELL_SIZE/2)
        self.brain.forget()
        self.see()
        self.brain.think(self)
    
    def move(self, destination) -> bool:
        if 0 <= destination.x < MAX_X and 0 <= destination.y < MAX_Y:
            self.current_location = destination
            self.expend_energy(1)
            return True
        return False

    def check_needs(self, need_type) -> bool:
        print(f"Dob #{self.id}, checked needs: 'food' = '{self.current_calories < self.dna["max_calories"] * 0.8}, 'water' = '{self.current_hydration < self.dna["max_hydration"] * 0.8}'")
        if need_type == "food":
            return self.current_calories < self.dna["max_calories"] * 0.8
        elif need_type == "water":
            return self.current_hydration < self.dna["max_hydration"] * 0.8
        return False

class Brain():
    def __init__(self):
        self.prioritized_thinking = [
            ("pursue", lambda dob: any(m["type"] == "need" and dob.check_needs(m["need_type"]) for m in self.short_term_memory["visible"])),
            ("wander", lambda dob: True),
        ]

        self.short_term_memory = {
            "visible": []
        }

        self.long_term_memory = []

    def think(self, dob):
        for thought, condition in self.prioritized_thinking:
            if condition(dob):
                if not thought == "wander":
                    print(f"Dob #{dob.id} chose to '{thought}'")
                getattr(dob, thought)()
                return

    def memorize(self, dob, target_memory, memory):
        already_seen = any(m["object"] == memory["object"] for m in self.short_term_memory["visible"])

        if target_memory == SHORT and not already_seen:
            memory["age"] = DOB_TRAITS["SHORT_TERM_AGE"]
            self.short_term_memory["visible"].append(memory)
        
            print(f"Dob #{dob.id} memorized {memory['object'].get_grid_coordinates()}!")

    def forget(self):
        for memory in self.short_term_memory["visible"]:
            memory["age"] -= 1
        
        self.short_term_memory["visible"] = [memory for memory in self.short_term_memory["visible"] if memory["age"] > 0]