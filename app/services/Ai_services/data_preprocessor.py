import numpy as np
import joblib
from pathlib import Path

class DataPreprocessor:
    def __init__(self):
        encoders_path = Path(__file__).parent.parent / "app" / "AI_model" / "label_encoders.joblib"
        self.label_encoders = joblib.load(encoders_path)

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