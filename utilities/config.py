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
STARTING_WATER_SOURCES = 6
CASCADE_CHANCE_REDUCTION = 0.01
WATER_VALUE = 10

# endregion

# region ----- DOBS -----

# Dob Constants
ACTIVE_DOBS = []
DOB = "dob"
REPRODUCTION = "reproduction"
SHORT_TERM_MEMORY = "short"
LONG_TERM_MEMORY = "long"
DOBAMINE = "dobamine"
FEMALE = "F"
MALE = "M"

# Dob Settings
STARTING_DOB_POPULATION = 10

DEFAULT_MAX_CALORIES = 1000
HUNGER_THRESHHOLD = 0.8
FOOD_COST = 5 # per move

DEFAULT_MAX_HYDRATION = 100
THIRST_THRESHHOLD = 0.8
WATER_COST = 1 # per move

DEFAULT_DOBAMINE = 100
LOW_DOBAMINE_THRESHHOLD = 0.4
HIGH_DOBAMINE_THRESHHOLD = 0.8
DOBAMINE_EXPLORATION_REWARD = 1

MEMORY_AGES = {
    SHORT_TERM_MEMORY: 20,
    LONG_TERM_MEMORY: 100,
}
FORGET_CHANCE_PER = 0.02 # per tick
INTERACTIONS_TO_PROMOTE = 2

# Age
AGE_RATE = 1 # per tick
BABY_DOB_SIZE = TILE_SIZE / 3
ADULT_DOB_SIZE = TILE_SIZE / 2
ADULT_AGE = 50
ELDER_AGE = 200
DEATH_AGE = 300

# Sex
FEMALE_COLOR = (155, 0, 255)
MALE_COLOR = (0, 10, 255)

# Mating
MATING_COOLDOWN = 10
MATING_COOLDOWN_SPEED = 0.5 # gained per tick
OFFSPRING_LIMIT = 2

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
