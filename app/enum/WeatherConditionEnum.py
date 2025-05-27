from enum import Enum

class WeatherCondition(str, Enum):
    SUNNY = "SUNNY"
    RAINY = "RAINY"
    WINDY = "WINDY"
    NORMAL = "NORMAL"

    def __str__(self):
            return self.value
