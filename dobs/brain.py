from utilities.config import *
from utilities.utils import *
from random import random, choice, choices

# TODO: Add aggressive vs passive search modes based on urgency
# TODO: Ponder orb and think how dobamine can affect urgencies
# TODO: Implement weight system (is this where dobamine goes?)
# TODO: Make a communication system so dobs can tell other dobs where food is
# TODO: Make dobs recognize food value and change their eating habits accordingly

# TODO: CLEAN THIS SHIT UP

# Local Config
COORDS = 0
VALUE = 1
DISTANCE_FROM = 2
DOBAMINE_GAIN = 3

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
        self.memory: dict[object, dict[str, int]] = {} # permanent object memory
        self.tile_memory = {} # coords (tuple[int, int])
        self.objects_in_sight = [] # objects
        self.tiles_in_sight = []
        self.bad_tiles = set()
    
    # Function called to determine what a dob is going to do
    def think(self) -> bool:
        new_goal = self.determine_goal()
        
        if not self.current_goal or not self.current_goal.get("coords"):
            self.current_goal = new_goal

        coords = self.current_goal.get("coords")
        target = self.current_goal.get("target")
        request = self.current_goal.get("request")

        # If the dob is adjacent to coords (target), interact with it
        if self.dob.is_adjacent_to(coords) and target and request:
            self.dob.interact(target, request)
            self.current_goal = {}
            return False

        if is_surrounded(coords, self.dob.grid_pos):
            return
        
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
        else:
            target, coords = None, None

        # TODO: Rework beyond this point! -------------------------------->
        # elif most_urgent == POPULATION_DENSITY:
        #     target, coords = None, self.dob.get_tile_in_sight(AGGRESSIVE_SEARCH)
        # elif most_urgent == DOBAMINE() and self.is_partnered():
        #     partner = self.is_partnered()
        #     target, coords = partner, partner.grid_pos
        #     request = COMMUNICATE 

        # If nothing was found, explore based on needs, unless it's a child, then it follows it's mom
        if not coords:
            if self.dob.mom and self.dob.age < ADULT_AGE:
                target, coords = self.dob.mom, self.dob.mom.grid_pos
            else:
                target, coords = None, self.search(most_urgent)

            if not coords:
                print(f"Dob ({self.dob.id}) has no coords!")
            request = None

        return {
            "target": target,
            "coords": coords,
            "request": request
        }
    
    def search(self, searching_for: str) -> tuple[int, int]:
        """Runs a search algorithm to determine best move relative to dob's circumstances"""

        # By default, if there are tagged tiles for what the dob is searching for, go to it
        tagged_tiles = self.get_tiles_in_sight_by_tag(searching_for)
        
        if tagged_tiles:
            tagged_tiles = self.evaluate_tiles(tagged_tiles)
            tagged_tiles = sorted(tagged_tiles, key=_tagged_key)
            return tagged_tiles[0][0]

        # Otherwise, the dob will get a list of tiles in sight and from memory
        potential_tiles = self.get_potential_tiles(searching_for)   # returns a list of tiles: [(x, y)]
        potential_tiles = self.evaluate_tiles(potential_tiles)  # returns a list of tile valuations: [(x, y), distance, etc.]

        # Search Values
        # [0] == coords
        # [1] == value
        # [2] == distance from dob
        # [3] == dobamine value (or a tile that has not been explored previously)

        confidence = self.get_confidence()
        needs = [FOOD, TREE, WATER]

        if confidence < HIGH_CONFIDENCE:
            if searching_for in needs:
                key = _wander_mode_key
            elif searching_for == DOBAMINE:
                key = _explore_mode_key
            else:
                return choice(potential_tiles)[0]
        
        elif confidence >= HIGH_CONFIDENCE:
            if searching_for in needs:
                key = _search_mode_key
            else:
                key = _comfort_mode_key

        sorted_tiles = sorted(potential_tiles, key=key)
        
        # selected_tile = randint(0, min(2, len(sorted_tiles) - 1))

        decay_rate = 0.45
        selection_weights = [50 * (decay_rate**i) for i in range(len(sorted_tiles))]
        selected_tile = choices(sorted_tiles, weights=selection_weights, k=1)[0]


        return selected_tile[0]
    
    def get_confidence(self) -> float:
        tile_matches = [tile for tile in self.tiles_in_sight if tile in self.get_tiles_from_memory()]
        return min(1.0, len(tile_matches) / len(self.tiles_in_sight)) if self.tiles_in_sight else 0.0

    ## Tile System
    # Tiles are valued and tagged by the dobs for movement in search()
    def get_potential_tiles(self, searching_for) -> list[tuple[int, int]]:
        """Returns a list of potential tiles for the search system"""
        tiles_from_memory = self.get_tiles_from_memory(searching_for)

        # If the dob is searching for a need, remove tiles that have alternate tags
        if searching_for in NEED_TAGS.keys():
            search_tags = NEED_TAGS[searching_for]
            in_sight = self.filter_tiles(self.tiles_in_sight, search_tags)
        
        # Otherwise, just return a list of tiles in sight that are not surrounded
        else:
            in_sight = self.filter_tiles(self.tiles_in_sight)
        
        return tiles_from_memory + in_sight
    
    def get_tiles_from_memory(self, tags_to_filter: list=[]) -> list[tuple[int, int]]: 
        """Returns a list of coordinates from memory, filtered"""
        return self.filter_tiles(list(self.tile_memory.keys()), tags_to_filter)
    
    def get_tiles_in_sight_by_tag(self, searching_for: str) -> list[tuple[int, int]]:
        """Returns a list of coordinates that share a tag,: searching_for"""
        tagged_tiles = []

        for tile, tile_information in self.tile_memory.items():
            if searching_for in tile_information.get("interests", []):
                tagged_tiles.append(tile)

        tagged_tiles = self.filter_tiles(tagged_tiles)

        return tagged_tiles  
    
    def evaluate_tiles(self, tiles: list) -> list:
        """Takes a list of tiles and returns a list of tile evaluations for search"""
        evaluated_tiles = []

        for tile in tiles:
            value = 0.0
            distance = self.dob.get_grid_distance_to(tile)
            dobamine_value = self.get_tile_dobamine_value(tile)

            if tile in self.tile_memory.keys():
                value = self.tile_memory[tile]["value"]

            evaluated_tiles.append((tile, value, distance, dobamine_value))
        
        return evaluated_tiles
    
    def filter_tiles(self, list_of_tiles: list, exclude_tiles_with_tags: list=[]) -> list:
        """Filters out tiles by tag and if they're surrounded"""
        return [tile for tile in list_of_tiles
                if not any(tag in self.tile_memory.get(tile, {}).get("interests", []) for tag in exclude_tiles_with_tags)
                and not is_surrounded(tile)
                and tile not in self.bad_tiles]
    
    def share_memory(self, target):
        # TODO: for memory in memory, get memory value to partner, share
        pass
    
    def get_chance_to_wander(self) -> float:
        """Get a dob's chance to wander, increases with lower dobamine"""
        minimum_cap = 0.2
        dobamine_ratio = 1 - (self.current_dobamine / self.max_dobamine)

        return max(minimum_cap, dobamine_ratio ** 2)

    # region ----- MEMORY FUNCTIONS -----

    def receive_tiles_in_sight(self, coords: list):
        self.tiles_in_sight = coords
        self.objects_in_sight.clear()
        interests_in_sight = set()

        for coord in coords:
            for obj in get_objects_at(coord):
                self.objects_in_sight.append(obj)
                if obj.tag != DOB:
                    interests_in_sight.add(obj.tag)
        
        self.evaluate_tile(list(interests_in_sight))

    def get_objects_in_sight(self, tag: str) -> list: # of objects
        return [obj for obj in self.objects_in_sight
                if obj.tag == tag
                and not is_surrounded(obj.grid_pos)]
    
    def evaluate_tile(self, interests: list):
        # TODO: Consider adding a slight increase if a dob FOUND a resource of value to them at that moment
        interest_value = {
            FOOD: 0.1,
            WATER: 0.5,
            TREE: 0.5
        }

        tile_value = sum(interest_value.get(tag, 0.1) for tag in interests)        
        self.save_tile_to_memory(tile_value, interests)
    
    def save_tile_to_memory(self, value: float, interests: list):
        self.tile_memory[self.dob.grid_pos] = {
            "value": value,
            "interests": interests
        }

    # TODO: Rework into a per tick decay of tile value
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
    def send_interaction(self, obj: object, interacts: int):
        if obj.tag == FOOD:
            obj = obj.tree

        self.memorize(obj, obj.tag, interactions=interacts)

    def memorize(self, object_to_be_memorized: object, tag: str, interactions: int=INTERACTIONS_TO_PROMOTE):
        """Memorizes an object by interaction, if interacts >= 10, the dob can use that as a consistent coordinate"""
        for object_in_memory in self.memory:
            if object_in_memory == object_to_be_memorized and interactions >= 10:
                self.memory[object_in_memory]["interactions"] += interactions
            elif object_in_memory == object_to_be_memorized:
                self.send_dobamine_gain()
                self.memory[object_to_be_memorized] = {
                    "tag": tag,
                    "interactions": interactions
                }

    # endregion
    
    # region ----- DOBAMINE FUNCTIONS -----

    def get_dobamine_decay(self) -> int:
        """Incrememts dobamine per tick in dob.exist()"""
        dobamine_gain = -5

        if self.is_food_secure():
            dobamine_gain += 1
        
        if self.is_water_secure():
            dobamine_gain += 1
        
        self.send_dobamine_gain(dobamine_gain)

    def get_tile_dobamine_value(self, coord: tuple[int, int]) -> int:
        if coord not in self.tile_memory.get(coord, []):
            return DOBAMINE_TILE_VALUE
        return 0
    
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
            # TODO: Increase bonus if partner
            nearby_mate = self.get_potential_mates()
            if nearby_mate:
                urgency = min(1.0, the_urge + NEARBY_MATE_BONUS)

            else:
                urgency = the_urge
        
        else:
            urgency = 0.0

        return urgency
    
    def get_potential_mates(self) -> list:
        """Analyzes nearby dobs to determine if they're a potential mate"""
        bad_matches = []

        for mem in self.memory:
            if mem["tag"] == "partner":
                return [mem["object"]]
            elif mem["tag"] == "bad_mate":
                bad_matches.append(mem["object"])
            
        return [obj for obj in self.objects_in_sight
                if obj.tag == DOB
                and obj.sex != self.dob.sex
                and not is_surrounded(obj.grid_pos)
                and obj.can_mate()
                and obj not in bad_matches
                and not obj.brain.is_partnered()]

    def get_closest_mate(self):
        """Gets the closest viable mate to the dob"""
        matches = self.get_potential_mates()

        if matches:
            target = min(matches, key=lambda m: self.dob.get_grid_distance_to(m.grid_pos))
            return target, target.grid_pos

        return None, None

    def remember_bad_mate(self, bad_mate: object):
        """Remembers a bad mate so they will not attempt mating again"""
        self.memorize(bad_mate, "bad_mate")
    
    def form_partnership(self, partner: object):
        self.memorize(partner, "partner")
    
    def is_partnered(self) -> object:
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
        self.dobamine_ratio = self.current_dobamine / self.max_dobamine

        self.thirst_urgency = 1 - self.thirst_ratio
        self.hunger_urgency = 1 - self.hunger_ratio
        self.dobamine_urgency = 1 - self.dobamine_ratio

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
            # POPULATION_DENSITY: self.determine_pop_density_urge(),
            DOBAMINE: self.determine_dobamine_needs() * 0.5
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
    
    def filter_objects(self, list_to_filter: list[object]) -> list:
        return [obj for obj in list_to_filter if obj.grid_pos not in self.bad_tiles]
    
    # endregion

    # region ----- FOOD BRAIN FUNCTIONS -----

    def get_closest_food(self) -> tuple[object, tuple[int, int]]:
        """Get the closet food to the dob"""
        matches = self.get_objects_in_sight(FOOD)
        matches = self.filter_objects(matches)

        if matches:
            target = min(matches, key=lambda m: self.dob.get_grid_distance_to(m.grid_pos))
            return target, target.grid_pos

        return None, None
    
    def is_food_secure(self) -> bool:
        """Checks if dob is higher than 40% calories"""
        return self.dob.current_calories > self.dob.max_calories * 0.4
    
    # endregion

    # region ----- WATER BRAIN FUNCTIONS -----

    def get_closest_water(self) -> tuple[object, tuple[int, int]]:
        """Get the closet water to the dob"""
        matches = self.get_objects_in_sight(WATER)
        matches = self.filter_objects(matches)

        # Since there's only one water object, it's actually checking the closest water tiles
        closest = None, None
        closest_dist = float('inf')
        
        for target in matches:
            for tile in target.water_positions:
                if tile in self.bad_tiles or is_surrounded(tile):
                    continue    
                dist = self.dob.get_grid_distance_to(tile)
                if dist < closest_dist:
                    closest_dist = dist
                    closest = target, tile

        return closest

    def is_water_secure(self) -> bool:
        """Checks if dob is higher than 40% hydration"""
        return self.dob.current_hydration > self.dob.max_hydration * 0.4
    
    
    # endregion

# region ----- LOCAL FUNCTIONS -----

        # Sort Variables
        # [0] == COORDS
        # [1] == VALUE
        # [2] == DISTANCE_FROM
        # [3] == DOBAMINE_TILE_VALUE

def _wander_mode_key(tile) -> tuple:
    """Sorts for far, unexplored tiles"""
    return (-tile[DISTANCE_FROM], -tile[DOBAMINE_TILE_VALUE])

def _explore_mode_key(tile) -> tuple:
    """Sorts for close, unexplored tiles"""
    return (tile[DISTANCE_FROM], -tile[DOBAMINE_TILE_VALUE])

def _search_mode_key(tile) -> tuple:
    """Sorts for high value, far tiles"""
    return (-tile[VALUE], -tile[DISTANCE_FROM])

def _comfort_mode_key(tile) -> tuple:
    """Sorts for high value, close tiles"""
    return (-tile[VALUE], tile[DISTANCE_FROM])

def _tagged_key(tile) -> tuple:
    return (-tile[VALUE], tile[DISTANCE_FROM])

# endregion