import pygame
from random import randrange
from config import MAX_X, MAX_Y, CELL_SIZE, ACTIVE_FOOD

class Dob():
    _id = 0

    def __init__(self):
        self.id = Dob._id
        Dob._id += 1

        self.brain = Brain()
        self.alive = True
        self.dna = {
            "calorie_need": 1000,
            "hydration_need": 50,
            "sight": 2,
        }

        self.random_spawn()

    def random_spawn(self):
        spawn_x = randrange(0, MAX_X, CELL_SIZE) + CELL_SIZE // 2
        spawn_y = randrange(0, MAX_Y, CELL_SIZE) + CELL_SIZE // 2
        self.current_location = pygame.Vector2(spawn_x, spawn_y)

    def wander(self):
        moved = False

        while not moved:
            x_change = randrange(-1, 2) * CELL_SIZE
            y_change = randrange(-1, 2) * CELL_SIZE

            new_position = self.current_location + pygame.Vector2(x_change, y_change)

            if 0 <= new_position.x < MAX_X and 0 <= new_position.y < MAX_Y:
                self.current_location = new_position
                self.expend_energy(1)
                moved = True

    def see(self, surface):
        grid_x = int(self.current_location.x // CELL_SIZE)
        grid_y = int(self.current_location.y // CELL_SIZE)
        sight_distance = self.dna["sight"]

        visible_tiles = []

        for x in range(grid_x - sight_distance, grid_x + sight_distance + 1):
            for y in range(grid_y - sight_distance, grid_y + sight_distance + 1):
                if 0 <= x < MAX_X // CELL_SIZE and 0 <= y < MAX_Y // CELL_SIZE:
                    visible_tiles.append((x, y))

        visible_food = [food for food in ACTIVE_FOOD if food.get_grid_location() in visible_tiles]

        if len(visible_food) > 0:
            for food in visible_food:
                memory = {
                    "type": "food",
                    "object": food
                }
                self.brain.memorize(self, "short", memory)
                print(f"Dob #{self.id} spotted food at {food.get_grid_location()}!")

        return visible_tiles

    def expend_energy(self, factor):
        self.dna["calorie_need"] -= 10 * factor
        self.dna["hydration_need"] -= 1 * factor

        if self.dna["calorie_need"] == 0 or self.dna["hydration_need"] == 0:
            # self.alive = False
            pass
        
    def exist(self, surface):
        pygame.draw.circle(surface, "blue", self.current_location, CELL_SIZE/2)
        self.see(surface)
        self.brain.think(self)

class Brain():
    def __init__(self):
        self.prioritized_thinking = [
            ("wander", lambda dob: True),
        ]

        self.short_term_memory = {
            "visible": []
        }

        self.long_term_memory = []

    def think(self, dob):
        for thought, condition in self.prioritized_thinking:
            if condition(dob):
                getattr(dob, thought)()
                break
        
        self.forget()

    def memorize(self, dob, target_memory, memory):
        if target_memory == "short":
            already_seen = any(m["object"] == memory["object"] for m in self.short_term_memory["visible"])
            if not already_seen:
                self.short_term_memory["visible"].append(memory)
            print(f"Dob #{dob.id} memorized {self.short_term_memory["visible"][0]["object"].get_grid_location()}")

    def forget(self):
        self.short_term_memory["visible"].clear()