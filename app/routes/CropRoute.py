from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import HTTPException
from app.services.CropService import CropService

crop_bp = Blueprint("crop", __name__, url_prefix="/lands/<land_id>/blocks/<block_id>/crops")

@crop_bp.route("", methods=["POST"])
@jwt_required()
def create_crop(land_id, block_id):
    try:
        data = request.get_json()

        crop_id = CropService.create_crop(
            crop_type=data["crop_type"],
            growth_state=data["growth_state"],
            planted_at=data.get("planted_at"),
            block_id=block_id
        )
        return jsonify({"crop_id": crop_id}), 201

    except HTTPException as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crop_bp.route("", methods=["GET"])
@jwt_required()
def list_crops(land_id, block_id):
    try:
        crops = CropService.find_by_block_id(block_id)
        return jsonify([crop.model_dump() for crop in crops]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crop_bp.route("/<crop_id>", methods=["GET"])
@jwt_required()
def get_crop(land_id, block_id, crop_id):
    try:
        crop = CropService.find_by_id(crop_id)
        return jsonify(crop.model_dump()), 200

    except HTTPException as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crop_bp.route("/<crop_id>", methods=["PUT"])
@jwt_required()
def update_crop(land_id, block_id, crop_id):
    try:
        data = request.get_json()
        CropService.update_crop(crop_id, data)
        return jsonify({"message": "Crop updated"}), 200

    except HTTPException as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crop_bp.route("/<crop_id>", methods=["DELETE"])
@jwt_required()
def delete_crop(land_id, block_id, crop_id):
    try:
        CropService.delete_crop(crop_id)
        return jsonify({"message": "Crop deleted"}), 200

    except HTTPException as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
