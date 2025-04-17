from app.database import mongo
from app.models.Crop import Crop
from bson import ObjectId
from datetime import datetime
from werkzeug.exceptions import NotFound, Conflict
from pydantic import ValidationError


class CropService:

    @staticmethod
    def create_crop(crop_type, growth_state, planted_at=None, block_id=None):
        try:
            if not block_id:
                raise ValueError("Crop must be assigned to a block")

            crop = Crop(
                crop_type=crop_type,
                growth_state=growth_state,
                planted_at=planted_at or datetime.now(datetime.timezone.utc),
                block_id=block_id
            )
            result = mongo.db.crops.insert_one(crop.model_dump(exclude={"id"}))
            return str(result.inserted_id)

        except ValidationError as e:
            raise Conflict(f"Invalid crop data: {e}")

    @staticmethod
    def find_by_id(crop_id: str) -> Crop:
        crop_data = mongo.db.crops.find_one({"_id": ObjectId(crop_id)})
        if not crop_data:
            raise NotFound("Crop not found")
        crop_data["id"] = str(crop_data["_id"])
        return Crop(**crop_data)

    @staticmethod
    def update_crop(crop_id: str, crop_data: dict):
        existing = mongo.db.crops.find_one({"_id": ObjectId(crop_id)})
        if not existing:
            raise NotFound("Crop not found")

        mongo.db.crops.update_one(
            {"_id": ObjectId(crop_id)},
            {"$set": crop_data}
        )

    @staticmethod
    def delete_crop(crop_id: str):
        result = mongo.db.crops.delete_one({"_id": ObjectId(crop_id)})
        if result.deleted_count == 0:
            raise NotFound("Crop not found")

    @staticmethod
    def find_by_block_id(block_id: str) -> list[Crop]:
        crop_docs = mongo.db.crops.find({"block_id": block_id})
        crops = []
        for doc in crop_docs:
            doc["id"] = str(doc["_id"])
            crops.append(Crop(**doc))
        return crops
