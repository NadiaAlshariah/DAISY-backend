from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from app.database import Base, db_session

class Prediction(Base):    
    def __init__(self, land_id, block_id, water_requirement, unit="mm/day", timestamp=None):
        import uuid
        self.id = str(uuid.uuid4())
        self.land_id = land_id
        self.block_id = block_id
        self.water_requirement = water_requirement
        self.unit = unit
        self.timestamp = timestamp or datetime.now()