from flask import Flask
from .config import Config
from .database import init_db, mongo
from flask_jwt_extended import JWTManager
from .routes.AuthRoute import auth_bp
from flask_pymongo import PyMongo

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    mongo.init_app(app, uri=app.config["MONGO_URI"])
    init_db(app)
    jwt = JWTManager(app) 
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    return app
