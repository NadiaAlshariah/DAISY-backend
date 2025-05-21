from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.BlockService import BlockService

block_bp = Blueprint("block", __name__, url_prefix="/lands/<land_id>/blocks")


@block_bp.route("/", methods=["GET"])
@jwt_required()
def get_blocks_by_land(land_id):
    blocks = BlockService.get_blocks_by_land_id(land_id)
    return jsonify([block.model_dump() for block in blocks]), 200


@block_bp.route("/<block_id>", methods=["GET"])
@jwt_required()
def get_block_by_id(land_id, block_id):
    block = BlockService.get_block_by_id(block_id)
    return jsonify(block.model_dump()), 200


@block_bp.route("/", methods=["POST"])
@jwt_required()
def create_block(land_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing JSON data"}), 400

    data["land_id"] = land_id
    block_id = BlockService.create_block(data)
    return jsonify({"block_id": block_id}), 201


@block_bp.route("/<block_id>", methods=["PUT"])
@jwt_required()
def update_block(land_id, block_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing JSON data"}), 400

    data["land_id"] = land_id 
    BlockService.update_block(block_id, data)
    return jsonify({"message": "Block updated"}), 200


@block_bp.route("/<block_id>", methods=["DELETE"])
@jwt_required()
def delete_block(land_id, block_id):
    try:
        BlockService.delete_block(block_id)
        return jsonify({"message": "Block deleted"}), 200
    except HTTPException as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    BlockService.delete_block(block_id)
    return jsonify({"message": "Block deleted"}), 200