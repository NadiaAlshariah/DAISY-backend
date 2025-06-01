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
            return str(result.inserted_id)

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


            sensor_id = data.get("sensor_id")
            if sensor_id:
                mongo.db.sensors.update_one(
                    {"_id": ObjectId(sensor_id)},
                    {"$set": {
                        "block_id": block_id,
                        "status": SensorStatus.CONNECTED.value
                    }}
                )
            
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
                }}
            )

        return True
