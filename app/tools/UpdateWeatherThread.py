from apscheduler.schedulers.background import BackgroundScheduler
from app.services.WeatherService import WeatherService
from app.database import mongo
from app.ml.irrigation.service.IrrigationMLService import IrrigationPredictionService
from app.ml.cropyield.service.YieldPredictionService import YieldPredictionService

from app.services.BlockService import BlockService


def update_weather_for_all_lands():
    irrigation_service = IrrigationPredictionService()
    yield_service = YieldPredictionService()

    lands = list(mongo.db.lands.find({}))

    for land in lands:
        lat = land.get("latitude")
        lon = land.get("longitude")
        land_id = land["_id"]

        try:
            weather_info = WeatherService.getCurrentWeatherInfo(lat, lon)

            condition_today = WeatherService.mapWeatherCondition(
                weather_info["condition"], weather_info["wind_ms"]
            )
            yield_condition = WeatherService.mapYieldWeatherCondition(
                weather_info["condition"], weather_info["wind_ms"]
            )
            new_temp = weather_info.get("temperature_c")

            update_doc = {
                "$set": {"weather_condition_today": condition_today},
                "$inc": {f"weather_history.{yield_condition}": 1},
            }
            if new_temp is not None:
                update_doc["$push"] = {"tempreture_c": new_temp}

            mongo.db.lands.update_one({"_id": land_id}, update_doc)
            print(f"✅ Updated land {land_id} → Today: {condition_today}, Yield weather: {yield_condition}, Temp: {new_temp}")

            # Block predictions (each in their own try-except)
            blocks = BlockService.get_blocks_by_land_id(str(land_id))
            for block in blocks:
                try:
                    prediction = irrigation_service.predict_by_block_id(block.id)
                    print(f"🌱 Irrigation for Block {block.id}: {prediction} mm/day")
                except Exception as e:
                    print(f"❌ Failed to predict irrigation for block {block.id}: {e}")

                try:
                    yield_prediction = yield_service.predict_by_block_id(block.id)
                    print(f"🌾 Yield for Block {block.id}: {yield_prediction.yield_tons_per_hectare} tons/hectare")
                except Exception as e:
                    print(f"❌ Failed to predict yield for block {block.id}: {e}")

        except Exception as e:
            print(f"❌ Failed to update weather for land {land_id}: {e}")

from datetime import datetime


def start_weather_scheduler(app):
    scheduler = BackgroundScheduler()

    @scheduler.scheduled_job('interval', minutes=10, next_run_time=datetime.now())
    def scheduled_job():
        with app.app_context():
            update_weather_for_all_lands()

    scheduler.start()
    print("sch_started")
