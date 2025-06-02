from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.BlockService import BlockService
from app.ml.cropyield.service.YieldPredictionService import YieldPredictionService
from app.ml.irrigation.service.IrrigationMLService import IrrigationPredictionService


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
    BlockService.delete_block(block_id)
    return jsonify({"message": "Block deleted"}), 200


@block_bp.route("/crop-distribution", methods=["GET"])
@jwt_required()
def get_crop_distribution_for_land(land_id):
    blocks = BlockService.get_blocks_by_land_id(land_id)

    crop_counts = {}
    total_blocks = 0

    for block in blocks:
        crop = block.crop_type
        crop_counts[crop] = crop_counts.get(crop, 0) + 1
        total_blocks += 1

    return jsonify({
        "total_blocks": total_blocks,
        "crop_distribution": crop_counts
    }), 200


@block_bp.route("/<block_id>/predict-yield", methods=["GET"])
@jwt_required()
def predict_yield_for_block(land_id, block_id):
    try:
        prediction = YieldPredictionService().get_latest_prediction_by_block_id(block_id)
        prediction_data = prediction.model_dump()

        tons_per_hectare = prediction_data.get("yield_tons_per_hectare", 0)
        kg_per_m2 = round(tons_per_hectare * 0.1, 3)
        prediction_data["yield_kg_per_m2"] = kg_per_m2
        prediction_data["yield_unit"] = "kg/m²"

        return jsonify(prediction_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@block_bp.route("/<block_id>/irrigation-predict", methods=["GET"])
@jwt_required()
def predict_irrigation_for_block(land_id, block_id):
    try:
        prediction = IrrigationPredictionService().get_latest_prediction_by_block_id(block_id)
        return jsonify(prediction.model_dump()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@block_bp.route("/<block_id>/irrigation-predict-history", methods=["GET"])
@jwt_required()
def get_all_irrigation_predictions_for_block(land_id, block_id):
    try:
        predictions = IrrigationPredictionService().get_all_predictions_by_block_id(block_id)
        return jsonify([p.model_dump() for p in predictions]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

      
@block_bp.route("/<block_id>/disconnect-sensor", methods=["POST"])
def disconnect_sensor(block_id):
    try:
        BlockService.disconnectSensor(block_id)
        return jsonify({"message": "Sensor disconnected from block successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    