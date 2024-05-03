import os
from pathlib import Path

# define configuration variables here

SCREEN_SIZE = (1366, 768)
LIB_PATH = Path(__file__).parent
ROOT_PATH = LIB_PATH.parent
RESOURCE_PATH = os.path.join(ROOT_PATH, "resources")

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
WHITE = (255, 255, 255)
