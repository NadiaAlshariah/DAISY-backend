from app.database import mongo
from app.models.Land import Land
from bson import ObjectId
from app.exception.BadRequestException import BadRequestException
from app.exception.NotFoundException import NotFoundException
from app.services.WeatherService import WeatherService


class LandService:
    @staticmethod
    def create_land(data: dict) -> str:
        try:
            latitude = data.get("latitude")
            longitude = data.get("longitude")

            weather_info = WeatherService.getCurrentWeatherInfo(latitude, longitude)

            condition_today = WeatherService.mapWeatherCondition(
                weather_info["condition"],
                weather_info["wind_ms"]
            )

            yield_condition = WeatherService.mapYieldWeatherCondition(
                weather_info["condition"],
                weather_info["wind_ms"]
            )

            temperature = weather_info.get("temperature_c")

            # ✅ Inject into data dict
            data["weather_condition_today"] = condition_today
            data["weather_history"] = {
                "Sunny": 0,
                "Rainy": 0,
                "Cloudy": 0,
                yield_condition: 1 
            }
            data["tempreture_c"] = [temperature] if temperature is not None else []

            land = Land(**data)
            result = mongo.db.lands.insert_one(land.model_dump(exclude={"id"}))
            return str(result.inserted_id)
        except Exception as e:
            raise BadRequestException(f"Error creating land: {e}")


    @staticmethod
    def get_land_by_id(land_id: str) -> Land:
        land_data = mongo.db.lands.find_one({"_id": ObjectId(land_id)})
        if not land_data:
            raise NotFoundException("Land not found")
        land_data["id"] = str(land_data["_id"])
        return Land(**land_data)

    @staticmethod
    def update_land(land_id: str, land_data: dict):
        existing = mongo.db.lands.find_one({"_id": ObjectId(land_id)})
        if not existing:
            raise NotFoundException("Land not found")

        mongo.db.lands.update_one(
            {"_id": ObjectId(land_id)},
            {"$set": land_data}
        )

    @staticmethod
    def delete_land(land_id: str):
        result = mongo.db.lands.delete_one({"_id": ObjectId(land_id)})
        if result.deleted_count == 0:
            raise NotFoundException("Land not found")
        
    @staticmethod
    def get_lands_by_user_id(user_id: str) -> list[Land]:
        lands = mongo.db.lands.find({"user_id": user_id})
       
        return [
            Land(**{**land, "id": str(land["_id"])})
            for land in lands
        ]

    @staticmethod
    def get_land_by_wifi_ssid(ssid : str):
        land = mongo.db.lands.find_one({"wifi_ssid" : ssid})
        if not land:
            raise NotFoundException("Land not found")
        return Land(**land)