# Food Constants
ACTIVE_FOOD = []
FOOD = "food"

# Food Settings
STARTING_FOOD_COUNT = 15
FOOD_REGROWTH_RATE = 50

# Water Constants
ACTIVE_WATER = []
WATER = "water"

# Water Settings
STARTING_WATER_SOURCES = 10

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
    "DEATH_AGE": 200,
}

# Age
MATING_COOLDOWN = 10
MATING_AGE = 50

# Data Settings
SNAPSHOT_FREQUENCY = 20

## UI Settings
# Settings are pixel
FPS = 60
CELL_SIZE = 20
MAX_X = 720
MAX_Y = 720

# General Constants
GRID_CARDINALS = [
    (1, 0),
    (-1, 0),
    (0, 1),
    (0, -1),
]

GRID_DIAGONALS = [
    (1, -1),
    (-1, -1),
    (-1, 1),
    (1, 1)
]