from enum import Enum

class SensorStatus(str, Enum):
    OFFLINE = "offline"  # turned off  
    CONNECTED = "connected" # connected to a block
    DISCONNECTED = "disconnected" # available to connect to a block