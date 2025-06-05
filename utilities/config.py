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
ACTIVE_FOOD = []
FOOD = "food"

# Food Settings
STARTING_FOOD_COUNT = 10
FOOD_REGROWTH_COOLDOWN = 50
FOOD_VALUE = 250

# endregion

# region ----- WATER -----

# Water Constants
ACTIVE_WATER = []
WATER = "water"

# Water Settings
STARTING_WATER_SOURCES = 5
CASCADE_CHANCE_REDUCTION = 0.01
WATER_VALUE = 15

# endregion

# region ----- DOBS -----

# Dob Constants
ACTIVE_DOBS = []
DOB = "dob"
REPRODUCTION = "reproduction"
SHORT_TERM = "short"
LONG_TERM = "long"
SHORT_TERM_MEMORY = "short"
LONG_TERM_MEMORY = "long"
DOBAMINE = "dobamine"

# Dob Settings
STARTING_DOB_POPULATION = 10

DEFAULT_MAX_CALORIES = 1000
HUNGER_THRESHHOLD = 0.8

DEFAULT_MAX_HYDRATION = 100
THIRST_THRESHHOLD = 0.8

DEFAULT_DOBAMINE = 100
LOW_DOBAMINE_THRESHHOLD = 0.4
HIGH_DOBAMINE_THRESHHOLD = 0.8
DOBAMINE_EXPLORATION_REWARD = 1

# Memory ages affect how long dobs remember things, removing 1 per tick
MEMORY_AGES = {
    "short": 10,
    "long": 500,
}

# Age
AGE_RATE = 1 # per tick
BABY_DOB_SIZE = TILE_SIZE / 3
ADULT_DOB_SIZE = TILE_SIZE / 2
ADULT_AGE = 50
ELDER_AGE = 150
DEATH_AGE = 200

# Colors
FEMALE_COLOR = (155, 0, 255)
MALE_COLOR = (0, 10, 255)

# Mating
MATING_COOLDOWN = 10
MATING_COOLDOWN_SPEED = 0.5 # gained per tick

# endregion

# region ----- DATA -----

# Data Settings
SNAPSHOT_FREQUENCY = 20

# endregion

# region ----- GENERAL -----

ACTIVE_OBJECTS = [ACTIVE_DOBS, ACTIVE_FOOD, ACTIVE_WATER]
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
