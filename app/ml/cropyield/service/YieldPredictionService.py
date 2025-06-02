import joblib
import pandas as pd
from pathlib import Path
from app.models.Block import Block
from app.models.Land import Land
from app.ml.cropyield.model.YieldPrediction import YieldPrediction
from app.services.BlockService import BlockService
from app.services.LandService import LandService
from app.database import mongo
from datetime import datetime, timezone


class YieldPredictionService:
    def __init__(self):
        base_path = Path(__file__).resolve().parent.parent
        self.model = joblib.load(base_path / "linear_regression_crop_yield_model.pkl")
        self.encoder = joblib.load(base_path / "encoder_for_crop_yield.pkl")

    def predict_by_block_id(self, block_id: str) -> YieldPrediction:
        block = BlockService.get_block_by_id(block_id)
        land = LandService.get_land_by_id(block.land_id)
        processed_df = self.preprocess_block_data(block, land)
        prediction = round(self.model.predict(processed_df)[0], 2)
        return self.save_prediction(block, land, prediction)


    def preprocess_block_data(self, block: Block, land: Land) -> pd.DataFrame:
        crop = block.crop_type if block.crop_type else "Wheat"
        soil_type = block.get_soil_texture()
        rainfall = block.rainfall_mm
        temperature = land.get_average_temperature()
        fertilizer_used = block.fertilizer_uesd
        irrigation_used = block.irrigation_used
        weather_condition = land.most_frequent_weather() or "NORMAL"
        region = "North"
        days_to_harvest = 140.0

        data = {
            "Region": region,
            "Soil_Type": soil_type,
            "Crop": crop,
            "Rainfall_mm": rainfall,
            "Temperature_Celsius": temperature,
            "Fertilizer_Used": fertilizer_used,
            "Irrigation_Used": irrigation_used,
            "Weather_Condition": weather_condition,
            "Days_to_Harvest": days_to_harvest
        }

        df = pd.DataFrame([data])

        categorical_cols = ['Region', 'Soil_Type', 'Crop', 'Weather_Condition']
        encoded = self.encoder.transform(df[categorical_cols])
        encoded_df = pd.DataFrame(encoded, columns=self.encoder.get_feature_names_out(), index=df.index)

        numeric_cols = ["Rainfall_mm", "Temperature_Celsius", "Fertilizer_Used", "Irrigation_Used", "Days_to_Harvest"]
        final_df = pd.concat([encoded_df, df[numeric_cols]], axis=1)

        expected_features = list(self.model.feature_names_in_)
        for col in expected_features:
            if col not in final_df.columns:
                final_df[col] = 0
        final_df = final_df[expected_features]

        return final_df


    def save_prediction(self, block: Block, land: Land, prediction: float) -> YieldPrediction:
        prediction_record = YieldPrediction(
            block_id=block.id,
            land_id=land.id,
            user_id=land.user_id,
            crop = block.crop_type if block.crop_type else "Wheat",
            soil_type = block.get_soil_texture(),
            rainfall = block.rainfall_mm,
            temperature = land.get_average_temperature(),
            fertilizer_used = block.fertilizer_uesd,
            irrigation_used = block.irrigation_used,
            weather_condition = land.most_frequent_weather() or "NORMAL",
            region = "North",
            days_to_harvest = 140.0,
            yield_tons_per_hectare=prediction,
            created_at=datetime.now(timezone.utc)
        )

        inserted = mongo.db.yield_predictions.insert_one(
            prediction_record.model_dump(exclude={"id"})
        )
        prediction_record.id = str(inserted.inserted_id)
        return prediction_record
    
    
    def get_latest_prediction_by_block_id(self, block_id: str) -> YieldPrediction | None:
        record = mongo.db.yield_predictions.find_one(
            {"block_id": block_id},
            sort=[("created_at", -1), ("_id", -1)]
        )

        if record:
            record["id"] = str(record["_id"])
            return YieldPrediction(**record)

        return self.predict_by_block_id(block_id)
        
    

    def get_latest_predictions_by_land_id(self, land_id: str) -> list[YieldPrediction]:
        blocks = BlockService.get_blocks_by_land_id(land_id)
        predictions = []

        for block in blocks:
            prediction = self.get_latest_prediction_by_block_id(block.id)
            if prediction:
                predictions.append(prediction)

        return predictions
    

    def get_latest_predictions_by_user_id(self, user_id: str) -> list[YieldPrediction]:
        lands = LandService.get_lands_by_user_id(user_id)
        predictions = []
    
        for land in lands:
            land_predictions = self.get_latest_predictions_by_land_id(land.id)
            predictions.extend(land_predictions)
    
        return predictions

