from enum import Enum

class Region(str, Enum):
    DESERT = "desert"
    SEMI_ARID = "semi arid"
    SEMI_HUMID = "semi humid"
    HUMID = "humid"