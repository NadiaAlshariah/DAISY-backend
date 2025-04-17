from enum import Enum

class GrowthState(str, Enum):
    SEED = "seed"
    GERMINATING = "germinating"
    VEGETATIVE = "vegetative"
    BUDDING = "budding"
    FLOWERING = "flowering"
    RIPENING = "ripening"
    HARVESTED = "harvested"