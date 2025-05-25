from enum import Enum

class WeatherCondition(str, Enum):
    NORMAL = "normal"
    SUNNY = "sunny"
    WINDY = "windy"
    RAINY = "rainy"
