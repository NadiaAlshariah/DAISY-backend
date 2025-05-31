from app.database import mongo
from app.models.Block import Block
from app.enum.SensorStatusEnum import SensorStatus
from bson import ObjectId
from app.exception.BadRequestException import BadRequestException
from app.exception.NotFoundException import NotFoundException
from pydantic import ValidationError

class BlockService:
    @staticmethod
    def create_block(data: dict) -> str:
        try:
            block = Block(**data)
            result = mongo.db.blocks.insert_one(block.model_dump(exclude={"id"}))
            block_id = str(result.inserted_id)

            BlockService.run_weather_and_predictions_for_block(block)

            return block_id

        except ValidationError as ve:
            raise BadRequestException(f"Invalid block data: {ve}")
        except Exception as e:
            raise Exception(f"Error creating block: {e}")


    @staticmethod
    def get_block_by_id(block_id: str) -> Block:
        block_data = mongo.db.blocks.find_one({"_id": ObjectId(block_id)})
        if not block_data:
            raise NotFoundException("Block not found")
        block_data["id"] = str(block_data["_id"])
        return Block(**block_data)

    @staticmethod
    def update_block(block_id: str, data: dict):
        existing = mongo.db.blocks.find_one({"_id": ObjectId(block_id)})
        if not existing:
            raise NotFoundException("Block not found")

        try:
            updated = {**existing, **data}
            validated_block = Block(**updated)
            update_dict = validated_block.model_dump(exclude={"id"})
            
            mongo.db.blocks.update_one(
                {"_id": ObjectId(block_id)},
                {"$set": update_dict}
            )
        except ValidationError as ve:
            raise BadRequestException(f"Invalid block update data: {ve}")
        except Exception as e:
            raise Exception(f"Error updating block: {e}")

    @staticmethod
    def delete_block(block_id: str):
        result = mongo.db.blocks.delete_one({"_id": ObjectId(block_id)})
        if result.deleted_count == 0:
            raise NotFoundException("Block not found")
        
    @staticmethod
    def get_blocks_by_land_id(land_id: str) -> list[Block]:
        blocks = mongo.db.blocks.find({"land_id": land_id})
        blocks_list = []
        for block_data in blocks:
            block_data["id"] = str(block_data["_id"])
            blocks_list.append(Block(**block_data))
        return blocks_list
    
    @staticmethod
    def disconnectSensor(block_id : str):
        block = mongo.db.blocks.find_one({"_id": ObjectId(block_id)})
        if not block:
            raise NotFoundException("Block not found")

        sensor_id = block.get("sensor_id")

        result = mongo.db.blocks.update_one(
            {"_id": ObjectId(block_id)},
            {"$set": {"sensor_id": None}}
        )
        if result.matched_count == 0:
            raise NotFoundException("Block not found")

        if sensor_id:
            mongo.db.sensors.update_one(
                {"_id": sensor_id},
                {"$set": {
                    "status": SensorStatus.DISCONNECTED.value,
                    "pin": -1
                }}
            )

        return True

    @staticmethod
    def run_weather_and_predictions_for_block(block: Block):
        from app.services.LandService import LandService
        from app.services.WeatherService import WeatherService
        from app.ml.irrigation.service.IrrigationMLService import IrrigationPredictionService
        from app.ml.cropyield.service.YieldPredictionService import YieldPredictionService

        try:
            land = LandService.get_land_by_id(block.land_id)
            BlockService._update_weather_info(land, WeatherService)
            BlockService._predict_irrigation(block.id, IrrigationPredictionService())
            BlockService._predict_yield(block.id, YieldPredictionService())
        except Exception as e:
            print(f"❌ Post-creation hook failed: {e}")

    @staticmethod
    def _update_weather_info(land, WeatherService):
        try:
            weather_info = WeatherService.getCurrentWeatherInfo(land.latitude, land.longitude)
            condition_today = WeatherService.mapWeatherCondition(weather_info["condition"], weather_info["wind_ms"])
            yield_condition = WeatherService.mapYieldWeatherCondition(weather_info["condition"], weather_info["wind_ms"])
            new_temp = weather_info.get("temperature_c")

            update_doc = {
                "$set": {"weather_condition_today": condition_today},
                "$inc": {f"weather_history.{yield_condition}": 1}
            }
            if new_temp is not None:
                update_doc["$push"] = {"tempreture_c": new_temp}

            mongo.db.lands.update_one({"_id": land.id}, update_doc)
            print(f"✅ Land {land.id} weather updated → {condition_today}, {yield_condition}, Temp: {new_temp}")

        except Exception as e:
            print(f"❌ Weather update failed for land {land.id}: {e}")

    @staticmethod
    def _predict_irrigation(block_id: str, service):
        try:
            prediction = service.predict_by_block_id(block_id)
            print(f"🌱 Irrigation → Block {block_id}: {prediction.water_requirement} mm/day")
        except Exception as e:
            print(f"❌ Irrigation prediction failed for block {block_id}: {e}")

    @staticmethod
    def _predict_yield(block_id: str, service):
        try:
            prediction = service.predict_by_block_id(block_id)
            print(f"🌾 Yield → Block {block_id}: {prediction.yield_tons_per_hectare} tons/hectare")
        except Exception as e:
            print(f"❌ Yield prediction failed for block {block_id}: {e}")