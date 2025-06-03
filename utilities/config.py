# ----- FOOD -----
# Food Constants
ACTIVE_FOOD = []
FOOD = "food"

# Food Settings
STARTING_FOOD_COUNT = 15
FOOD_REGROWTH_COOLDOWN = 50
FOOD_VALUE = 250

# ----- WATER -----
# Water Constants
ACTIVE_WATER = []
WATER = "water"

# Water Settings
STARTING_WATER_SOURCES = 10
CASCADE_CHANCE_REDUCTION = 0.02
WATER_VALUE = 20

# ----- DOBS -----
# Dob Constants
ACTIVE_DOBS = []
DOB = "dob"
REPRODUCTION = "reproduction"
SHORT_TERM = "short"
LONG_TERM = "long"

## Dob Settings
STARTING_DOB_POPULATION = 10

DOB_TRAITS = {
    # Memory ages -> affect how long dobs remember things
    "short": 5,
    "long": 500,
    # Dob color changes based on sex
    "F": "#006EFF",
    "M": "#001EFF",
}

# Age
AGE_RATE = 1
DOB_DEATH_AGE = 200

# Mating
MATING_AGE = 50
MATING_COOLDOWN = 10
MATING_COOLDOWN_SPEED = 0.5

# ----- DATA -----
# Data Settings
SNAPSHOT_FREQUENCY = 20

# ----- UTILITY -----
# UI Settings
TPS = 10
CELL_SIZE = 20
MAX_X = 720
MAX_Y = 720
MAX_GRID_X = MAX_X // CELL_SIZE
MAX_GRID_Y = MAX_Y // CELL_SIZE

# General Constants
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