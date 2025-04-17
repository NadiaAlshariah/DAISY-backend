from enum import Enum

# Enum for Crop Types
class CropType(str, Enum):
    WHEAT = "wheat"
    CORN = "corn"
    RICE = "rice"
    POTATO = "potato"