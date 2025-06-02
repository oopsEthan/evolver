# UI Settings
FPS = 60
CELL_SIZE = 20
MAX_X = 720
MAX_Y = 720

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
DOB_DB = []
DOB = "dob"
REPRODUCTION = "reproduction"

## Dob Settings
STARTING_DOB_POPULATION = 10

DOB_TRAITS = {
    # Memory ages affect how long dobs remember things
    "SHORT_TERM_AGE": 5,
    "LONG_TERM_AGE": 25,
    # Dob color changes based on sex
    "F": "#006EFF",
    "M": "#001EFF",
    "DEATH_AGE": 200,
}

# Age
DEFAULT_SEX_DRIVE = 15
MATING_AGE = 50

# Data Settings
SNAPSHOT_FREQUENCY = 20