from app.database import mongo
from app.models.Land import Land
from bson import ObjectId
from werkzeug.exceptions import NotFound, Conflict

class LandService:
    COLLECTION = mongo.db.lands

    @staticmethod
    def create_land(current_humidity: float, current_temperature: float) -> str:
        try:
            land = Land(
                current_humidity=current_humidity,
                current_temperature=current_temperature,
            )
            result = LandService.COLLECTION.insert_one(land.model_dump(exclude={"id"}))
            return str(result.inserted_id)

        except Exception as e:
            raise Conflict(f"Error creating land: {e}")

    @staticmethod
    def get_land_by_id(land_id: str) -> Land:
        land_data = LandService.COLLECTION.find_one({"_id": ObjectId(land_id)})
        if not land_data:
            raise NotFound("Land not found")
        land_data["id"] = str(land_data["_id"])
        return Land(**land_data)

    @staticmethod
    def update_land(land_id: str, land_data: dict):
        existing = LandService.COLLECTION.find_one({"_id": ObjectId(land_id)})
        if not existing:
            raise NotFound("Land not found")

        LandService.COLLECTION.update_one(
            {"_id": ObjectId(land_id)},
            {"$set": land_data}
        )

    @staticmethod
    def delete_land(land_id: str):
        """
        Delete a land object from the database.
        """
        result = LandService.COLLECTION.delete_one({"_id": ObjectId(land_id)})
        if result.deleted_count == 0:
            raise NotFound("Land not found")
