import threading
import time
from flask import Flask
from .config import Config
from .database import init_db, mongo
from flask_jwt_extended import JWTManager
from .routes.AuthRoute import auth_bp
from app.routes.LandRoute import land_bp
from app.routes.BlockRoute import block_bp
from app.routes.SensorRoute import sensors_bp
from flask import Flask, jsonify
from app.exception.BadRequestException import BadRequestException
from werkzeug.exceptions import HTTPException
from app.tools.UpdateWeatherThread import start_weather_scheduler
from datetime import datetime, timedelta
from bson import ObjectId
from app.enum.SensorStatusEnum import SensorStatus

def mark_sensors_offline():
    print("[Background] Sensor offline checker started.")
    while True:
        print("[Background] Checking for offline sensors...")
        cutoff = datetime.now() - timedelta(minutes=20)
        offline_sensors = list(mongo.db.sensors.find({
            "last_heartbeat": {"$lt": cutoff},
            "status": {"$ne": SensorStatus.OFFLINE.value}
        }))
        sensor_ids = [s["_id"] for s in offline_sensors]
        if sensor_ids:
            mongo.db.sensors.update_many(
                {"_id": {"$in": sensor_ids}},
                {"$set": {"status": SensorStatus.OFFLINE.value}}
            )
            print(f"[Background] Marked {len(sensor_ids)} sensors as OFFLINE.")
        else:
            print("[Background] No offline sensors found this cycle.")
        time.sleep(60)



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    mongo.init_app(app, uri=app.config["MONGO_URI"])
    init_db(app)
    jwt = JWTManager(app) 
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(land_bp)
    app.register_blueprint(block_bp)
    app.register_blueprint(sensors_bp)

    # Register Exception Handlers
    @app.errorhandler(BadRequestException)
    def handle_user_error(e):
        return jsonify({"error": e.message}), 400
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        response = e.get_response()
        return jsonify({
            "error": e.name,
            "message": e.description,
            "code": e.code
        }), e.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        return jsonify({"error": str(e)}), 500
    

    with app.app_context():
        start_weather_scheduler(app)
    
    threading.Thread(target=mark_sensors_offline, daemon=True).start()

    return app
