# app/services/PredictionService.py
import joblib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any
from app.models.prediction import PredictionModel
from app.services.BlockService import BlockService
from app import mongo
from app.services.Ai_services.data_preprocessor import DataPreprocessor 

class PredictionService:
    def __init__(self):
        model_path = Path(__file__).parent.parent / "AI_model" / "xgboost_irrigation_model.joblib"
        self.model = joblib.load(model_path)
        self.preprocessor = DataPreprocessor()

    def predict(self, input_data: dict) -> float:
        processed_input = self.preprocessor.preprocess_input(input_data)
        prediction_value = self.model.predict(processed_input)[0]
        return round(prediction_value, 2)

    def predict_and_save(self, land_id: str, block_id: str, input_data: dict) -> Dict[str, Any]:
        prediction_value = self.predict(input_data)

        prediction = PredictionModel(
            land_id=land_id,
            block_id=block_id,
            water_requirement=prediction_value
        )
        mongo.db.predictions.insert_one(prediction.to_dict())

        cutoff = datetime.utcnow() - timedelta(days=7)
        mongo.db.predictions.delete_many({
            "land_id": land_id,
            "timestamp": {"$lt": cutoff}
        })

        return {
            "land_id": land_id,
            "block_id": block_id,
            "water_requirement": prediction_value,
            "unit": "mm/day",
            "timestamp": prediction.timestamp.isoformat()
        }

    def get_irrigation_history(self, land_id: str, limit: int = 5) -> Dict[str, Any]:
        blocks = BlockService.get_blocks_by_land_id(land_id)
        history_data = {
            "land_id": land_id,
            "blocks": []
        }

        for block in blocks:
            block_id = block.id
            results = mongo.db.predictions.find(
                {"land_id": land_id, "block_id": block_id}
            ).sort("timestamp", -1).limit(limit)

            predictions = []
            for pred in results:
                predictions.append({
                    "prediction_id": str(pred.get("_id")),
                    "water_requirement": pred.get("water_requirement"),
                    "unit": pred.get("unit"),
                    "timestamp": pred.get("timestamp").isoformat()
                })

            history_data["blocks"].append({
                "block_id": block_id,
                "predictions": predictions
            })
        
        return history_data
