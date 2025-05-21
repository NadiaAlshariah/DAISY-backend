from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import HTTPException
from app.services.BlockService import BlockService

block_bp = Blueprint("block", __name__, url_prefix="/lands/<land_id>/blocks")

@block_bp.route("/", methods=["GET"])
@jwt_required()
def get_blocks_by_land(land_id):
    try:
        blocks = BlockService.get_blocks_by_land_id(land_id)
        return jsonify([block.model_dump() for block in blocks]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@block_bp.route("/<block_id>", methods=["GET"])
@jwt_required()
def get_block_by_id(land_id, block_id):
    try:
        block = BlockService.get_block_by_id(block_id)
        return jsonify(block.model_dump()), 200
    except HTTPException as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@block_bp.route("/create", methods=["POST"])
@jwt_required()
def create_block(land_id):
    try:
        data = request.get_json()

        block_id = BlockService.create_block(
            location=data["location"],
            land_id=land_id,
            current_soil_moisture=data["current_soil_moisture"],
            soil_type=data["soil_type"]
        )
        return jsonify({"block_id": block_id}), 201

    except HTTPException as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@block_bp.route("/<block_id>", methods=["PUT"])
@jwt_required()
def update_block(land_id, block_id):
    try:
        data = request.get_json()
        BlockService.update_block(block_id, data)
        return jsonify({"message": "Block updated"}), 200
    except HTTPException as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
    

