from datetime import datetime, timezone
import joblib
from pathlib import Path
from app.models.Block import Block
from app.models.Land import Land
from app.services.BlockService import BlockService
from app.services.LandService import LandService
import pandas as pd
from app.ml.irrigation.model.IrrigationPrediction import IrrigationPrediciton
from app.database import mongo


class IrrigationPredictionService:
    def __init__(self):
        base_path = Path(__file__).resolve().parent.parent
        self.model = joblib.load(base_path / "irrigation_model.pkl")
        self.label_encoders = joblib.load(base_path / "label_encoders.pkl")
        self.one_hot_encoder = joblib.load(base_path / "one_hot_encoder.pkl")
        self.scaler = joblib.load(base_path / "minmax_scaler.pkl")
        self.zscore_stats = joblib.load(base_path / "zscore_stats.pkl") 


    def predict_by_block_id(self, block_id: str) -> IrrigationPrediciton:
        block = BlockService.get_block_by_id(block_id)
        land = LandService.get_land_by_id(block.land_id)
        processed = self.preprocess_block_data(block, land)
        prediction_value = round(self.model.predict(processed)[0], 2)

        return self.save_prediction(block, land, prediction_value)
    

    def save_prediction(self, block: Block, land: Land, prediction: float) -> IrrigationPrediciton:
        soil_type = block.get_soil_type_category()
        temp_category = self.map_temperature_range(land.get_latest_temperature())
        crop_type = block.crop_type if block.crop_type else "WHEAT"
        region = land.get_region_enum().value
        weather_condition = land.weather_condition_today.value if land.weather_condition_today else "NORMAL"

        prediction_record = IrrigationPrediciton(
            block_id=block.id,
            land_id=land.id,
            user_id=land.user_id,
            soil_type=soil_type,
            crop_type=crop_type.upper(),
            region=region,
            tempreture=temp_category,
            weather_condition=weather_condition,
            water_requirement=str(prediction),
            created_at=datetime.now(timezone.utc)
        )

        inserted = mongo.db.irrigation_predictions.insert_one(
            prediction_record.model_dump(exclude={"id"})
        )
        prediction_record.id = str(inserted.inserted_id)

        return prediction_record


    def preprocess_block_data(self, block: Block, land: Land) -> pd.DataFrame:
        # Prepare raw input
        soil_type = block.get_soil_type_category()
        temp_category = self.map_temperature_range(land.get_latest_temperature())
        crop_type = block.crop_type if block.crop_type else "WHEAT"
        region = land.get_region_enum().value
        weather_condition = land.weather_condition_today.value if land.weather_condition_today else "NORMAL"

        raw_data = {
            "CROP TYPE": crop_type.upper(),
            "SOIL TYPE": soil_type,
            "REGION": region,
            "TEMPERATURE": temp_category,
            "WEATHER CONDITION": weather_condition
        }

        df = pd.DataFrame([raw_data])

        for col in ['SOIL TYPE', 'TEMPERATURE', 'REGION']:
            df[col] = self.label_encoders[col].transform(df[col])

        one_hot_input = df[['CROP TYPE', 'WEATHER CONDITION']]
        one_hot_array = self.one_hot_encoder.transform(one_hot_input)
        expected_cols = self.one_hot_encoder.get_feature_names_out()
        one_hot_df = pd.DataFrame(one_hot_array, columns=expected_cols)

        final_df = pd.concat([df[['SOIL TYPE', 'TEMPERATURE', 'REGION']], one_hot_df], axis=1)

        # Step 5: Drop any Z_ columns (safety guard)
        final_df = final_df[[col for col in final_df.columns if not col.startswith("Z_")]]

        # Step 6: Align with scaler/model input
        expected_features = self.scaler.feature_names_in_
        for col in expected_features:
            if col not in final_df.columns:
                final_df[col] = 0  # add missing columns

        final_df = final_df[expected_features]  # ensure order and remove extras

        # Step 7: Apply scaler
        scaled_array = self.scaler.transform(final_df)
        scaled_df = pd.DataFrame(scaled_array, columns=final_df.columns)

        return scaled_df
    

    def get_latest_prediction_by_block_id(self, block_id: str) -> IrrigationPrediciton:
        record = mongo.db.irrigation_predictions.find_one(
            {"block_id": block_id},
            sort=[("created_at", -1), ("_id", -1)]
        )
        if record:
            record["id"] = str(record["_id"])
            return IrrigationPrediciton(**record)
        return self.predict_by_block_id(block_id)


    def get_latest_prediction_by_land_id(self, land_id: str) -> IrrigationPrediciton:
        blocks = BlockService.get_blocks_by_land_id(land_id)
        total_water = 0.0
        last_preds = []

        for block in blocks:
            prediction = self.get_latest_prediction_by_block_id(block.id)
            total_water += float(prediction.water_requirement)
            last_preds.append(prediction)

        latest_created = max(p.created_at for p in last_preds)
        return IrrigationPrediciton(
            block_id="ALL",
            land_id=land_id,
            user_id=last_preds[0].user_id if last_preds else "",
            soil_type="mixed",
            crop_type="mixed",
            region="mixed",
            tempreture="mixed",
            weather_condition="mixed",
            water_requirement=str(round(total_water, 2)),
            created_at=latest_created
        )
    

    def get_all_predictions_by_land_id(self, land_id: str) -> tuple[list[IrrigationPrediciton], IrrigationPrediciton]:
        blocks = BlockService.get_blocks_by_land_id(land_id)
        all_preds = []

        for block in blocks:
            block_preds = self.get_all_predictions_by_block_id(block.id)
            all_preds.extend(block_preds)

        if not all_preds:
            raise Exception("No predictions found for this land.")

        total_water = sum(float(p.water_requirement) for p in all_preds)
        latest_created = max(p.created_at for p in all_preds)

        summary = IrrigationPrediciton(
            block_id="ALL",
            land_id=land_id,
            user_id=all_preds[0].user_id,
            soil_type="mixed",
            crop_type="mixed",
            region="mixed",
            tempreture="mixed",
            weather_condition="mixed",
            water_requirement=str(round(total_water, 2)),
            created_at=latest_created
        )

        return all_preds, summary


    def get_latest_predictions_summary_by_user_id(self, user_id: str) -> IrrigationPrediciton:
        lands = LandService.get_lands_by_user_id(user_id)
        total_water = 0.0
        all_predictions = []

        for land in lands:
            blocks = BlockService.get_blocks_by_land_id(land.id)
            for block in blocks:
                prediction = self.get_latest_prediction_by_block_id(block.id)
                total_water += float(prediction.water_requirement)
                all_predictions.append(prediction)

        if not all_predictions:
            raise Exception("No predictions available for this user.")

        latest_created = max(p.created_at for p in all_predictions)

        return IrrigationPrediciton(
            block_id="ALL",
            land_id="ALL",
            user_id=user_id,
            soil_type="mixed",
            crop_type="mixed",
            region="mixed",
            tempreture="mixed",
            weather_condition="mixed",
            water_requirement=str(round(total_water, 2)),
            created_at=latest_created
        )
    

    def get_all_predictions_summary_by_user_id(self, user_id: str) -> tuple[list[IrrigationPrediciton], IrrigationPrediciton]:
        lands = LandService.get_lands_by_user_id(user_id)
        all_predictions = []

        for land in lands:
            blocks = BlockService.get_blocks_by_land_id(land.id)
            for block in blocks:
                block_predictions = self.get_all_predictions_by_block_id(block.id)
                all_predictions.extend(block_predictions)

        if not all_predictions:
            raise Exception("No predictions found for user.")

        total_water = sum(float(p.water_requirement) for p in all_predictions)
        latest_created = max(p.created_at for p in all_predictions)

        summary = IrrigationPrediciton(
            block_id="ALL",
            land_id="ALL",
            user_id=user_id,
            soil_type="mixed",
            crop_type="mixed",
            region="mixed",
            tempreture="mixed",
            weather_condition="mixed",
            water_requirement=str(round(total_water, 2)),
            created_at=latest_created
        )

        return all_predictions, summary



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
        return "unknown"
