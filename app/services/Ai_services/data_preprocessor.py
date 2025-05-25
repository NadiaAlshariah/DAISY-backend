import numpy as np
import joblib
from pathlib import Path

class DataPreprocessor:
    def __init__(self):
        encoders_path = Path(__file__).parent.parent / "app" / "AI_model" / "label_encoders.joblib"
        self.label_encoders = joblib.load(encoders_path)


    @staticmethod
    def map_temperature_range(temp: float) -> str:
        if temp is None:
            return "unknown"
        if -100 <= temp < 20:
            return "10-20"
        elif 20 <= temp < 30:
            return "20-30"
        elif 30 <= temp < 40:
            return "30-40"
        elif 40 <= temp <= 60:
            return "40-50"


    def map_weather_condition(description: str, wind_speed: float) -> str:
        if wind_speed > 7.0:
            return "WINDY"
        
        if any(word in description for word in ["rain", "thunderstorm", "shower", "snow", "mist", "drizzle"]):
            return "RAINY"
        elif "clear" in description:
            return "SUNNY"
        elif any(word in description for word in ["cloud", "overcast", "haze"]):
            return "NORMAL"
        else:
            return "NORMAL"
        
    
    def classify_soil_type(soil_moisture: float) -> str:
        if soil_moisture < 15:
            return "DRY"
        elif soil_moisture < 35:
            return "HUMID"
        else:
            return "WET"


    def preprocess_input(self, input_data: dict) -> np.ndarray:
        encoded_data = {}
        for col, value in input_data.items():
            if col in self.label_encoders:
                encoded_data[col] = self.label_encoders[col].transform([value])[0]
            else:
                encoded_data[col] = value

        feature_order = [
            'temperature', 'humidity', 'wind_speed', 'evapotranspiration',
            'soil_moisture_levels', 'water_retention_capacity',
            'crop_water_requirement', 'rainfall_pattern', 'soil_type',
            'drainage_properties', 'crop_type', 'growth_stage'
        ]
        return np.array([[encoded_data[col] for col in feature_order]])