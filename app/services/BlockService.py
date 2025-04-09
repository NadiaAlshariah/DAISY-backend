from app.database import mongo
from app.models.Block import Block
from bson import ObjectId
from werkzeug.exceptions import NotFound, Conflict
from datetime import datetime

class BlockService:
    COLLECTION = mongo.db.blocks

    @staticmethod
    def create_block(location: str, land_id: str, current_soil_moisture: float, soil_type: str) -> str:
        try:
            block = Block(
                location=location,
                land_id=land_id,
                current_soil_moisture=current_soil_moisture,
                soil_type=soil_type
            )
            result = BlockService.COLLECTION.insert_one(block.model_dump(exclude={"id"}))
            return str(result.inserted_id)

        except Exception as e:
            raise Conflict(f"Error creating block: {e}")

    @staticmethod
    def get_block_by_id(block_id: str) -> Block:
        block_data = BlockService.COLLECTION.find_one({"_id": ObjectId(block_id)})
        if not block_data:
            raise NotFound("Block not found")
        block_data["id"] = str(block_data["_id"])
        return Block(**block_data)

    @staticmethod
    def update_block(block_id: str, block_data: dict):
        existing = BlockService.COLLECTION.find_one({"_id": ObjectId(block_id)})
        if not existing:
            raise NotFound("Block not found")

        BlockService.COLLECTION.update_one(
            {"_id": ObjectId(block_id)},
            {"$set": block_data}
        )

    @staticmethod
    def delete_block(block_id: str):
        result = BlockService.COLLECTION.delete_one({"_id": ObjectId(block_id)})
        if result.deleted_count == 0:
            raise NotFound("Block not found")
        
    @staticmethod
    def get_blocks_by_land_id(land_id: str) -> list[Block]:
        blocks = mongo.db.blocks.find({"land_id": land_id})
        blocks_list = []
        for block_data in blocks:
            block_data["id"] = str(block_data["_id"])
            blocks_list.append(Block(**block_data))
        return blocks_list
