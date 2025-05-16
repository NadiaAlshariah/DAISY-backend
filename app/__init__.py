from flask import Flask
from .config import Config
from .database import init_db, mongo
from flask_jwt_extended import JWTManager
from .routes.AuthRoute import auth_bp
from app.routes.LandRoute import land_bp
from app.routes.CropRoute import crop_bp
from app.routes.BlockRoute import block_bp
from flask import Flask, jsonify
from app.exception.BadRequestException import BadRequestException

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
    app.register_blueprint(crop_bp)

    # Register Exception Handlers
    @app.errorhandler(BadRequestException)
    def handle_user_error(e):
        return jsonify({"error": e.message}), 400

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        print(e.message)
        return jsonify({"Internal server error "}), 500
    
    return app
