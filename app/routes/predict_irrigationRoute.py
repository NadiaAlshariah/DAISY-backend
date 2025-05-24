from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import HTTPException, BadRequest
from app.services.LandService import LandService
from app.services.BlockService import BlockService
from app.services.Ai_services.prediction_service import PredictionService
from app.services.WeatherService import WeatherService
from app.models.CropModel import CropModel
from datetime import datetime

predict_bp = Blueprint("predict", __name__, url_prefix="/predict")

@predict_bp.route("/<land_id>/predict_irrigation", methods=["POST"])
@jwt_required()
def predict_irrigationRoute(land_id):
    try:
        user_id = get_jwt_identity()
        land = LandService.get_land_by_id(land_id)
        blocks = BlockService.get_blocks_by_land_id(land_id)

        if not blocks:
            return jsonify({"error": "No blocks found for this land"}), 404

        selected_block = next((b for b in blocks if b.get("crops")), None)
        if not selected_block:
            return jsonify({"error": "No blocks with crops found"}), 400

        selected_crop = selected_block["crops"][0]
        selected_crop = CropModel(**raw_crop)

        weatherData = WeatherService.getCurrentWeatherInfo(land.latitude, land.longitude,datetime.now().hour)
        if "error" in weatherData:
            return jsonify({"error": f"Weather data error: {weatherData['error']}"}), 500
        
        input_data = {
            "temperature": weatherData.get("temperature_c"),
            "humidity": weatherData.get("humidity"),
            "wind_speed": weatherData.get("wind_ms"),
            "evapotranspiration": weatherData.get("evapotranspiration"),
            "rainfall_pattern": weatherData.get("rainfall_pattern").value,
            "soil_moisture_levels": selected_block["current_soil_moisture"],
            "water_retention_capacity": selected_block["water_retention_capacity"],
            "soil_type": selected_block["soil_type"].value,
            "drainage_properties": selected_block["drainage_properties"].value,
            "crop_type": selected_crop.crop_type.value,
            "growth_stage": selected_crop.growth_state.value,
            "crop_water_requirement": selected_crop.crop_water_requirement
        }
        required_fields = [
            'temperature', 'humidity', 'wind_speed', 'evapotranspiration',
            'soil_moisture_levels', 'water_retention_capacity', 'crop_type',
            'growth_stage', 'crop_water_requirement', 'rainfall_pattern',
            'soil_type', 'drainage_properties'
        ]

        missing = [field for field in required_fields if input_data.get(field) is None]
        if missing:
            return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

        result = PredictionService().predict_and_save(land_id, selected_block["id"], input_data)
        return jsonify(result), 200

    except HTTPException as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@predict_bp.route("/<land_id>/irrigation_history", methods=["GET"])
@jwt_required()
def get_irrigationHistory(land_id):
    try:
        user_id = get_jwt_identity()
        history = PredictionService().get_irrigation_history(land_id)
        return jsonify(history), 200
    except HTTPException as e:
        return jsonify({"error": str(e)}), e.code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
