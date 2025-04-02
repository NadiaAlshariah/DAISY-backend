from flask import Flask
from .config import Config
from .database import init_db
from flask_jwt_extended import JWTManager
from .routes.AuthRoute import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_db(app)
    jwt = JWTManager(app) 
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    return app
