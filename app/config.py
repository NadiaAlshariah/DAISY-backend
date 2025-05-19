import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES")))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES")))
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")