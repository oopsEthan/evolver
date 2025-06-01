# UI Constants
FPS = 10
CELL_SIZE = 20
MAX_X = 1280
MAX_Y = 720

# Global Variables
STARTING_DOB_POPULATION = 10
ACTIVE_DOBS = []
DOB = "dob"

STARTING_FOOD_COUNT = 30
ACTIVE_FOOD = []
FOOD_REGROWTH_RATE = 50
FOOD = "food"

STARTING_WATER_SOURCES = 30
ACTIVE_WATER = []
WATER = "water"

# Dob Constants
DOB_TRAITS = {
    "SHORT_TERM_AGE": 5,
    "LONG_TERM_AGE": 25,
    # Dob color changes based on sex
    "F": "#006EFF",
    "M": "#001EFF",
    "DEATH_AGE": 2000,
}
REPRODUCTION = "reproduction"
DEFAULT_SEX_DRIVE = 10
MATING_AGE = 30