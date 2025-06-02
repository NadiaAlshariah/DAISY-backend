from flask import Blueprint, request, jsonify
from app.services.LandService import LandService
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.BlockService import BlockService
from datetime import datetime
from app.services.WeatherService import WeatherService
from app.exception.BadRequestException import BadRequestException
from app.ml.cropyield.service.YieldPredictionService import YieldPredictionService
from app.ml.irrigation.service.IrrigationMLService import IrrigationPredictionService


land_bp = Blueprint("land", __name__, url_prefix="/lands")

@land_bp.route("/<land_id>", methods=["GET"])
@jwt_required()
def get_land_by_id(land_id):
    land = LandService.get_land_by_id(land_id)
    return jsonify(land.model_dump()), 200
    

@land_bp.route("/list", methods=["GET"])
@jwt_required()
def get_lands_by_user():
    user_id = get_jwt_identity()
    lands = LandService.get_lands_by_user_id(user_id)
    return jsonify([land.model_dump() for land in lands]), 200


@land_bp.route("/create", methods=["POST"])
@jwt_required()
def create_land():
    jwt_user_id = get_jwt_identity()

    data = request.get_json()
    data["user_id"] = jwt_user_id

    land_id = LandService.create_land(data)
    return jsonify({"land_id": land_id}), 201


@land_bp.route("/<land_id>", methods=["PUT"])
@jwt_required()
def edit_land(land_id):
    data = request.get_json()
    LandService.update_land(land_id, data)
    return jsonify({"message": "Land updated"}), 200

@land_bp.route("/<land_id>", methods=["DELETE"])
@jwt_required
def delete_land(land_id):
    LandService.delete_land(land_id)
    return jsonify({"message": "Land deleted"}), 200


@land_bp.route('/crop-distribution', methods=['GET'])
@jwt_required()
def get_crop_distribution():
    user_id = get_jwt_identity()
    lands = LandService.get_lands_by_user_id(user_id)

    crop_counts = {}
    total_blocks = 0

    for land in lands:
        blocks = BlockService.get_blocks_by_land_id(land.id)
        for block in blocks:
            crop = block.crop_type
            crop_counts[crop] = crop_counts.get(crop, 0) + 1
            total_blocks += 1

    return jsonify({
        "total_blocks": total_blocks,
        "crop_distribution": crop_counts
    }), 200


@land_bp.route("/<land_id>/weather", methods=["GET"])
@jwt_required()
def get_weather_by_land_id(land_id):
    hour = datetime.now().hour 
    land = LandService.get_land_by_id(land_id)
    
    if not land or not land.latitude or not land.longitude:
        raise BadRequestException("Land not found or missing coordinates.")
    
    weather_info = WeatherService.getCurrentWeatherInfo(land.latitude, land.longitude)
    return jsonify(weather_info), 200


@land_bp.route("/<land_id>/predict-yield", methods=["GET"])
@jwt_required()
def predict_yield_for_land(land_id):
    try:
        predictions = YieldPredictionService().get_latest_predictions_by_land_id(land_id)
        result = []

        for prediction in predictions:
            data = prediction.model_dump()
            tons_per_hectare = data.get("yield_tons_per_hectare", 0)
            data["yield_kg_per_m2"] = round(tons_per_hectare * 0.1, 3)
            data["yield_unit"] = "kg/m²"
            result.append(data)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@land_bp.route("/user/predict-yield", methods=["GET"])
@jwt_required()
def predict_yield_for_user():
    try:
        user_id = get_jwt_identity()
        predictions = YieldPredictionService().get_latest_predictions_by_user_id(user_id)
        result = []

        for prediction in predictions:
            data = prediction.model_dump()
            tons_per_hectare = data.get("yield_tons_per_hectare", 0)
            data["yield_kg_per_m2"] = round(tons_per_hectare * 0.1, 3)
            data["yield_unit"] = "kg/m²"
            result.append(data)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

prediction_service = IrrigationPredictionService()

@land_bp.route("/<land_id>/water-summary", methods=["GET"])
@jwt_required()
def get_water_summary_by_land(land_id):
    summary = prediction_service.calculate_water_summary_by_land_id(land_id)
    return jsonify(summary), 200
   
@land_bp.route("/user/water-summary", methods=["GET"])
@jwt_required()
def get_water_summary_by_user():
    user_id = get_jwt_identity()
    summary = prediction_service.calculate_water_summary_by_user_id(user_id)
    return jsonify(summary), 200

