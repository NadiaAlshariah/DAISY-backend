import joblib
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from .data_preprocessor import DataPreprocessor
from app.models.Block import Block 
from app.models.Prediction import Prediction 
from app.services.BlockService import BlockService

class PredictionService:
    def __init__(self):
        model_path = Path(__file__).parent.parent / "AI_model" / "xgboost_irrigation_model.joblib"
        self.model = joblib.load(model_path)
        self.preprocessor = DataPreprocessor()

    def predict(self, input_data: dict) -> float:
        processed_input = self.preprocessor.preprocess_input(input_data)
        prediction_value = self.model.predict(processed_input)[0]
        
        return round(prediction_value, 2)
    
    def save_prediction(self, land_id: str, block_id: str, prediction_value: float) -> None:
        prediction = Prediction(
            land_id=land_id,
            block_id=block_id,
            water_requirement=prediction_value,
            unit="mm/day",
            timestamp=datetime.now()
        )
        
        # should maybe save last week or a 5 days only 
        prediction.save()
        cutoff_date = datetime.now() - timedelta(days=7)
        Prediction.query.filter(
            Prediction.land_id == land_id,
            Prediction.timestamp < cutoff_date
        ).delete()
        
        return prediction

    def get_irrigation_history(self, land_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        blocks = BlockService.get_blocks_by_land_id(land_id)
        
        history_data = {
            "land_id": land_id,
            "blocks": []
        }
        
        for block in blocks:
            block_id = block.id
            predictions = Prediction.query.filter_by(
                land_id=land_id,
                block_id=block_id
            ).order_by(Prediction.timestamp.desc()).limit(limit).all()
            
            prediction_history = []
            for pred in predictions:
                prediction_history.append({
                    "prediction_id": pred.id,
                    "water_requirement": pred.water_requirement,
                    "unit": pred.unit,
                    "timestamp": pred.timestamp.isoformat(),
                })
            
            block_data = {
                "block_id": block_id,
                "predictions": prediction_history
            }
            
            history_data["blocks"].append(block_data)
        
        return history_data
    
    def predict_and_save(self, land_id: str, block_id: str, input_data: dict) -> Dict[str, Any]:
        prediction_value = self.predict(input_data)
        prediction = self.save_prediction(land_id, block_id, prediction_value)
        
        return {
            "land_id": land_id,
            "block_id": block_id,
            "water_requirement": prediction_value,
            "unit": "mm/day",
            "prediction_id": prediction.id,
            "timestamp": prediction.timestamp.isoformat()
        }