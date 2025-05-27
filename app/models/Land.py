from pydantic import BaseModel
from typing import Optional, List, Dict
from app.enum.RegionEnum import Region
from app.enum.WeatherConditionEnum import WeatherCondition
from pydantic import Field
from statistics import mean


class Land(BaseModel):
    id: Optional[str] = None
    user_id: str
    latitude : float
    longitude : float
    sensors: Optional[List[str]] = []
    wifi_ssid : Optional[str] = None
    name: str
    region: str
    weather_condition_today: Optional[WeatherCondition] = None
    weather_history: Optional[Dict[str, int]] = Field(default_factory=lambda: {"Sunny": 0, "Rainy": 0, "Cloudy": 0})
    tempreture_c: Optional[list[float]] = Field(default_factory=list)

    class Config:
        extra = "ignore"


    def get_region_enum(self) -> Region:
        return Region.from_friendly(self.region)
    

    def record_weather(self, condition: str):
        if condition in self.weather_history:
            self.weather_history[condition] += 1
        else:
            self.weather_history[condition] = 1  


    def most_frequent_weather(self) -> Optional[str]:
        if not self.weather_history:
            return None
        return max(self.weather_history.items(), key=lambda x: x[1])[0]
    
    
    def get_latest_temperature(self) -> Optional[float]:
        if not self.tempreture_c:
            return None
        return self.tempreture_c[-1]
    

    def get_average_temperature(self) -> Optional[float]:
        if not self.tempreture_c:
            return None
        return mean(self.tempreture_c)
    
