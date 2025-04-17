from enum import Enum

class SoilType(str, Enum):
    SANDY = "sandy"
    CLAY = "clay"
    LOAMY = "loamy"
    PEATY = "peaty"
    CHALKY = "chalky"