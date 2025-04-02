from flask_pymongo import PyMongo
from datetime import timedelta

mongo = PyMongo()
def init_db(app):
    mongo.init_app(app)
    if not app.config.get("MONGO_URI"):
        raise ValueError("MONGO_URI is not set in Config. Check your .env file.")
    # Create indexes
    with app.app_context():
        if not mongo.db:
            raise RuntimeError("MongoDB connection failed. Check your MONGO_URI and MongoDB server.")

        mongo.db.refresh_tokens.create_index(
            "created_at",
            expireAfterSeconds=int(timedelta(days=7).total_seconds())
        )
        mongo.db.users.create_index("email", unique=True)