from flask import Flask
from app.config import Config
from app.database import mongo

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mongo.init_app(app)

    return app
