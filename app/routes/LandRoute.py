from flask import Blueprint, request, jsonify
from app.services.LandService import LandService
from werkzeug.exceptions import HTTPException
from flask_jwt_extended import jwt_required, get_jwt_identity

land_bp = Blueprint("land", __name__, url_prefix="/lands")

@land_bp.route("/<land_id>", methods=["GET"])
@jwt_required()
def get_land_by_id(land_id):
    try:
        land = LandService.get_land_by_id(land_id)
        return jsonify(land.model_dump()), 200
    except HTTPException as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@land_bp.route("/list", methods=["GET"])
@jwt_required()
def get_lands_by_user():
    try:
        user_id = get_jwt_identity()
        lands = LandService.get_lands_by_user_id(user_id)
        return jsonify([land.model_dump() for land in lands]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@land_bp.route("/create", methods=["POST"])
@jwt_required()
def create_land():
    try:
        jwt_user_id = get_jwt_identity()
        data = request.get_json()

        land_id = LandService.create_land(
            current_humidity=data["current_humidity"],
            current_temperature=data["current_temperature"],
            user_id=jwt_user_id
        )
        return jsonify({"land_id": land_id}), 201
    except HTTPException as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@land_bp.route("/<land_id>", methods=["PUT"])
@jwt_required()
def edit_land(land_id):
    try:
        data = request.get_json()
        LandService.update_land(land_id, data)
        return jsonify({"message": "Land updated"}), 200
    except HTTPException as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@land_bp.route("/<land_id>", methods=["DELETE"])
@jwt_required
def delete_land(land_id):
    try:
        LandService.delete_land(land_id)
        return jsonify({"message": "Land deleted"}), 200
    except HTTPException as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
