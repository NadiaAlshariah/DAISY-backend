from flask import Blueprint, request, jsonify
from app.services.SensorService import SensorService
from app.enum.SensorStatusEnum import SensorStatus
from app.services.BlockService import BlockService
from app.ml.irrigation.service.IrrigationMLService import IrrigationPredictionService

sensors_bp = Blueprint('sensors', __name__)

@sensors_bp.route('/update-soil-moisture-predict', methods=['POST'])
def update_soil_moisture_and_predict():
    data = request.get_json()
    sensor = SensorService.getSensorByMacAndPin(data["mac_address"], data["pin"])
    print(sensor)
    prediction_service = IrrigationPredictionService()
    prediction =  prediction_service.predict_by_block_id(sensor.block_id)
    return jsonify({"prediction": float(prediction)})


@sensors_bp.route('/block/<block_id>', methods=['GET'])
def get_sensor_by_block_id(block_id):
    sensor = SensorService.getSensorsByBlockId(block_id)
    return jsonify(sensor.model_dump())

#example  :  /land/6835eac9ec3a1a5189a498ba
@sensors_bp.route('/land/<land_id>', methods=['GET'])
def get_sensors_by_land_id(land_id):
    sensors = SensorService.getSensorsByLandId(land_id)
    return jsonify([sensor.model_dump() for sensor in sensors])


@sensors_bp.route('/register', methods=['POST'])
def register_sensor():
    data = request.get_json()
    ssid = data.get('ssid')
    sensor_data = {k: v for k, v in data.items() if k != 'ssid'}
    sensor_id = SensorService.registerSensor(ssid, sensor_data)
    return jsonify({'sensor_id': sensor_id}), 201


@sensors_bp.route('/land/<land_id>/status/<status>', methods=['GET'])
def get_sensors_by_status(land_id, status):
    status_enum = SensorStatus(status)
    sensors = SensorService.getSensorByStatus(land_id, status_enum)
    return jsonify([sensor.model_dump() for sensor in sensors])


@sensors_bp.route('/heartbeat', methods=['PUT'])
def update_heartbeat():
    data = request.get_json()
    mac_address = data.get('mac_address')
    pin = data.get('pin')
    SensorService.updateHeartBeat(mac_address, pin)
    return jsonify({'success': True})