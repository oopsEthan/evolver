import pygame
from random import randrange, random, randint, choice
from utilities.config import *
from utilities.utils import *

# God of all objects, they are made in His image
class Simulation_Object:
    def __init__(self):
        self.grid_pos = (0, 0)
        self.pixel_pos = None
        self.move_to()

        self.energy_value = 0

    def move_to(self, loc: tuple=None) -> None:
        """Moves a simulation object to loc (x,y) on the grid, if no loc provided, random"""
        if not loc:
            while True:
                loc = randrange(0, MAX_GRID_X), randrange(0, MAX_GRID_Y)
                if not tile_occupied(loc):
                    break
        
        self.pixel_pos, self.grid_pos = relocate_object_on_GO(self, loc)
    
    def get_grid_distance_to(self, coords: tuple[int, int]) -> int:
        """Gets the grid distance between object and the target"""
        gx, gy = self.grid_pos
        tx, ty = coords
        return abs(gx - tx) + abs(gy - ty)

    def is_adjacent_to(self, coords: tuple[int,int]) -> bool:
        """Checks if the target is adjacent to the object"""
        if not coords:
            return False
        
        tx, ty = coords
        dx, dy = self.grid_pos
        return abs(tx - dx) + abs(ty - dy) == 1

    # Indicate what happens when a dob interacts with the object, by default it returns an energy value
    def interact_with(self, request):
        return True

    def register(self, object_class: object, object_tag: str, db: list=None) -> None:
        """Registers the object to the simulation"""
        self.id = object_class._id
        object_class._id += 1

        self.tag = object_tag

        if db is not None:
            self.db = db
            db.append(self)

class Food_Tree(Simulation_Object):
    _id = 0

    def __init__(self, starting_coords):
        super().__init__()
        self.register(Food_Tree, TREE, db=ACTIVE_TREES)
        self.move_to(self.adjust_spawn(starting_coords))

        self.grown_foods = []
        self.create_initial_growth()
        self.regrowth_chance = DEFAULT_FOOD_REGROWTH_CHANCE

    def exist(self, surface):
        pygame.draw.circle(surface, "brown", self.pixel_pos, TILE_SIZE/2)

        if len(self.grown_foods) < FOOD_TREE_MAX:
            self.attempt_to_grow()
        
        for food in self.grown_foods:
            food.exist(surface)
    
    def attempt_to_grow(self):
        roll = random()

        if roll < self.regrowth_chance:
            self.grow_food()
            self.regrowth_chance = DEFAULT_FOOD_REGROWTH_CHANCE
            return False
        
        self.regrowth_chance += 0.01
        return True

    def get_growth_spot(self) -> tuple[int, int]:
        potential_spots = get_adjacent_tiles(self.grid_pos, diagonals=False, avoid_occupied=True)
        if not potential_spots:
            print(f"{self.id} has no potential grow spots!")
            return None
        return choice(potential_spots)

    def create_initial_growth(self):
        for _ in range(FOOD_TREE_MAX):
            self.grow_food(skip=True)
    
    def grow_food(self, skip: bool=False):
        coords = self.get_growth_spot()

        for food in self.grown_foods:
            if food.grid_pos == coords:
                print(f"⚠️ Skipping growth at {coords} — already have Food ({food.id}) there")
                return
        
        food = Food(starting_coords=coords, designated_tree=self, skip_growth=skip)
        self.grown_foods.append(food)
    
    def adjust_spawn(self, coords):
        adjacents = get_adjacent_tiles(coords, diagonals=False, avoid_occupied=False)
        valid = [tile for tile in adjacents if within_bounds(tile) and not tile_occupied(tile)]

        if not valid:
            return None
        
        if len(valid) <= 2:
            return self.adjust_spawn(choice(valid))

        return choice(valid)
    
# Food is food that you eat food eat food
class Food(Simulation_Object):
    _id = 0

    def __init__(self, starting_coords, designated_tree, skip_growth=False):
        super().__init__()
        self.register(Food, FOOD)
        self.move_to(starting_coords)
        self.tree = designated_tree
        self.size = 4
        self.regrowth_chance = DEFAULT_FOOD_REGROWTH_CHANCE
        self.energy_value = MIN_FOOD_VALUE

        if skip_growth:
            self.energy_value = MAX_FOOD_VALUE
            self.size = 2

    def exist(self, surface):
        pygame.draw.circle(surface, "red", self.pixel_pos, TILE_SIZE/self.size)
        self.increase_value()

    # Food has to mark itself as eaten :(
    def interact_with(self):
        if self.tree is None:
            return False

        remove_object_from_GO(self)
        self.tree.grown_foods.remove(self)

        self.tree = None
        return super().interact_with()

    def increase_value(self):
        if self.energy_value < MAX_FOOD_VALUE:
            self.energy_value += FOOD_GROWTH_SPEED

            ratio = (MAX_FOOD_VALUE - self.energy_value) / (MAX_FOOD_VALUE - MIN_FOOD_VALUE)

            # size ∈ [2, 4], inversely scaled with energy_value
            self.size = 2 + (4 - 2) * ratio  # or: self.size = 2 + 2 * ratio

# Worter
class Water(Simulation_Object):
    _id = 0

    def __init__(self, starting_coords, chance_to_cascade=1):
        super().__init__()
        self.register(Water, WATER, db=ACTIVE_WATER)
        self.move_to(starting_coords)

        self.energy_value = WATER_VALUE
        
        self.water_positions = []
        self.cascade(chance_to_cascade, starting_coords)

    # Water is a Rect so it requires it's pixel-position to be adjusted by half a grid
    def exist(self, surface):
        offset_position = self.pixel_pos - pygame.Vector2(TILE_SIZE // 2, TILE_SIZE // 2)
        position = pygame.Rect(offset_position, GRID_UNIT)
        pygame.draw.rect(surface, "#47CBED", position)
        self.draw_water(surface) #6DD1EA
    
    # Water attempts to cascade to simulate ponds, rivers, etc.
    # If water cascades, the water it spawns will also attempt to cascade
    def cascade(self, chance, coords):
        if chance <= 0:
            return
        
        if random() <= chance:
            dx, dy = choice(GRID_CARDINALS)
            gx, gy = coords

            new_coords = (gx + dx, gy + dy)

            if tile_occupied(new_coords):
                self.cascade(chance, coords)

            if not tile_occupied(new_coords) and within_bounds(new_coords):
                add_object_to_GO(self, new_coords)
                self.water_positions.append(new_coords)
                self.cascade(chance - CASCADE_CHANCE_REDUCTION, new_coords)

    def draw_water(self, surface):
        for w in self.water_positions:
            offset_position = to_pixel(w) - pygame.Vector2(TILE_SIZE // 2, TILE_SIZE // 2)
            position = pygame.Rect(offset_position, GRID_UNIT)
            pygame.draw.rect(surface, "#5CCFEC", position)