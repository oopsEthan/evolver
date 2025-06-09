# region ----- UTILITY -----

# UI Settings
TPS = 10
MAX_X = 720
MAX_Y = 720
TILE_SIZE = 20
GRID_UNIT = (TILE_SIZE, TILE_SIZE)
MAX_GRID_X = MAX_X // TILE_SIZE
MAX_GRID_Y = MAX_Y // TILE_SIZE

# endregion

# region  ----- FOOD -----

# Food Constants
ACTIVE_TREES = []
TREE = "tree"
FOOD = "food"

# Food Settings
STARTING_TREE_COUNT = 5
FOOD_TREE_MAX = 3 
DEFAULT_FOOD_REGROWTH_CHANCE = -0.05 # % per tick
FOOD_GROWTH_SPEED = 5 # per tick
MIN_FOOD_VALUE = 150
MAX_FOOD_VALUE = 300

# endregion

# region ----- WATER -----

# Water Constants
ACTIVE_WATER = []
WATER = "water"

# Water Settings
STARTING_WATER_SOURCES = 8
CASCADE_CHANCE_REDUCTION = 0.01
WATER_VALUE = 50

# endregion

# region ----- DOBS -----

## Dob Constants
ACTIVE_DOBS = []
DOB = "dob"
REPRODUCTION = "reproduction"
# Memory
SHORT_TERM_MEMORY = "short"
LONG_TERM_MEMORY = "long"
PERMANENT_TERM_MEMORY = "permanent"
DOBAMINE = "dobamine"
AGGRESSIVE_SEARCH = "aggressive_needs"
AGGRESSIVE_EXPLORE = "aggressive_dobamine"
PASSIVE = "passive"
POPULATION_DENSITY = "population_density"
# Needs
NEED_TAGS = {
    FOOD: [FOOD, TREE],
    WATER: [WATER],
    REPRODUCTION: [REPRODUCTION],
    DOBAMINE: [DOBAMINE]
}
# Requests
EAT = "eat"
MATE = "mate"
COMMUNICATE = "communicate"
EXPLORE = "explore"

HIGH_CONFIDENCE = 0.5

# Sex
FEMALE = "F"
MALE = "M"

# Dob Settings
STARTING_DOB_POPULATION = 10

DEFAULT_MAX_CALORIES = 1000
DEFAULT_CALORIES_MOD = (-15, 30) # random mutation

HUNGER_THRESHHOLD = 0.8
FOOD_MULTIPLIER = 2.5 # multiply below
# 50 for mating
# 10 for moving
# 5 per 5 ticks

DEFAULT_MAX_HYDRATION = 100
DEFAULT_WATER_MOD = (-3, 5) # random mutation

THIRST_THRESHHOLD = 0.8
WATER_MULTIPLIER = 1 # multiply below
# 2-3 for mating
# 1 for else

DEFAULT_DOBAMINE = 100
LOW_DOBAMINE_THRESHHOLD = 0.4
HIGH_DOBAMINE_THRESHHOLD = 0.8
DOBAMINE_TILE_VALUE = 1

CROWDING_THRESHHOLD = 0.4 # % of vision tiles have dobs, triggers population density urge
CROWDING_SCALING = 2 # controls how much the crowding urgency scales if over crowding threshhold

# Danger threshhhold determines at what % calories a dob will start aggressively searching
DANGER_THRESHHOLD = 0.3

MEMORY_AGES = {
    SHORT_TERM_MEMORY: 20,
    LONG_TERM_MEMORY: 150,
    PERMANENT_TERM_MEMORY: 1,
}

FORGET_CHANCE_PER = 0.02 # per tick
INTERACTIONS_TO_PROMOTE = 10

# Age
AGE_RATE = 1 # per tick
BABY_DOB_SIZE = TILE_SIZE / 3
ADULT_DOB_SIZE = TILE_SIZE / 2
ADULT_AGE = 50
DEFAULT_ELDER_AGE = 200
TICKS_DOBS_LIVE_AT_ELDER_AGE = 70

DEFAULT_DEATH_AGE = 300
DEATH_AGE_MOD = (-5, 10) # random mutation

# Sex
FEMALE_COLOR = (155, 0, 255)
MALE_COLOR = (0, 10, 255)
COLOR_VARIATION = (-2, +2)

# Mating
MATING_COOLDOWN = 15
MATING_COOLDOWN_SPEED = 0.5 # gained per tick
NEARBY_MATE_BONUS = 0.2 # increases urge to reproduce if there's a nearby mate
OFFSPRING_LIMIT = 3

# endregion

# region ----- DATA -----

# Data Settings
SNAPSHOT_FREQUENCY = 50

# endregion

# region ----- GENERAL -----

GRID_OCCUPANCY = {}

# Cardinal directions on grid
NORTH = (0, 1)
SOUTH = (0, -1)
EAST = (1, 0)
WEST = (-1, 0)
GRID_CARDINALS = [
    NORTH,
    EAST,
    SOUTH,
    WEST
]

# Diagonal directions on grid
NORTHEAST = (1, 1)
SOUTHEAST = (1, -1)
SOUTHWEST = (-1, -1)
NORTHWEST = (-1, 1)
GRID_DIAGONALS = [
    NORTHEAST,
    SOUTHEAST,
    SOUTHWEST,
    NORTHWEST
]

# endregion
