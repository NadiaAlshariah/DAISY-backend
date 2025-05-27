from enum import Enum

class Region(str, Enum):
    DESERT = "DESERT"
    SEMI_ARID = "SEMI ARID"
    SEMI_HUMID = "SEMI HUMID"
    HUMID = "HUMID"

    def __str__(self):
        return self.value

    @classmethod
    def from_friendly(cls, user_input: str) -> "Region":
        friendly_map = {
            # Desert
            "desert": cls.DESERT,
            "drylands": cls.DESERT,
            "sahara": cls.DESERT,

            # Semi-arid
            "steppe": cls.SEMI_ARID,
            "semi dry": cls.SEMI_ARID,
            "plateau": cls.SEMI_ARID,

            # Semi-humid
            "forest": cls.SEMI_HUMID,
            "grassland": cls.SEMI_HUMID,
            "tropical": cls.SEMI_HUMID,

            # Humid
            "coastal": cls.HUMID,
            "rainforest": cls.HUMID,
            "wetland": cls.HUMID,
            "river basin": cls.HUMID,
            "mountain": cls.HUMID,
        }

        key = user_input.strip().lower()
        if key not in friendly_map:
            raise ValueError(
                f"Invalid region name '{user_input}'. "
                f"Expected one of: {', '.join(friendly_map.keys())}"
            )
        return friendly_map[key]
