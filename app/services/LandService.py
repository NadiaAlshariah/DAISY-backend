from app.database import mongo
from app.models.Land import Land
from bson import ObjectId
from werkzeug.exceptions import NotFound, Conflict

class LandService:

    @staticmethod
    def create_land(current_humidity: float, current_temperature: float, user_id: str) -> str:
        try:
            land = Land(
                current_humidity=current_humidity,
                current_temperature=current_temperature,
                user_id=user_id
            )
            result = mongo.db.lands.insert_one(land.model_dump(exclude={"id"}))
            return str(result.inserted_id)

        except Exception as e:
            raise Conflict(f"Error creating land: {e}")

    @staticmethod
    def get_land_by_id(land_id: str) -> Land:
        land_data = mongo.db.lands.find_one({"_id": ObjectId(land_id)})
        if not land_data:
            raise NotFound("Land not found")
        land_data["id"] = str(land_data["_id"])
        return Land(**land_data)

    @staticmethod
    def update_land(land_id: str, land_data: dict):
        existing = mongo.db.lands.find_one({"_id": ObjectId(land_id)})
        if not existing:
            raise NotFound("Land not found")

        mongo.db.lands.update_one(
            {"_id": ObjectId(land_id)},
            {"$set": land_data}
        )

    @staticmethod
    def delete_land(land_id: str):
        """
        Delete a land object from the database.
        """
        result = mongo.db.lands.delete_one({"_id": ObjectId(land_id)})
        if result.deleted_count == 0:
            raise NotFound("Land not found")
        
    @staticmethod
    def get_lands_by_user_id(user_id: str) -> list[Land]:
        lands = mongo.db.lands.find({"user_id": user_id})
        return [
            Land(**{**land, "id": str(land["_id"])})
            for land in lands
        ]
