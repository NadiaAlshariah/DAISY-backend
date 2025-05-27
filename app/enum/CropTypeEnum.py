from enum import Enum

class CropType(str, Enum):
    COTTON = "Cotton"
    RICE = "Rice"
    WHEAT = "Wheat"
    CORN = "Corn"

    def __str__(self):
        return self.value
