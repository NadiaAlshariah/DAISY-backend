from app.database import mongo
from app.exception.BadRequestException import BadRequestException
from app.exception.NotFoundException import NotFoundException
from app.models.Sensor import Sensor
from app.enum.SensorStatusEnum import SensorStatus
from app.services.LandService import LandService
from pydantic import ValidationError
from datetime import datetime


class SensorService:
    @staticmethod
    def getSensorsByBlockId(block_id: str):
        sensor = mongo.db.sensors.find_one({"block_id": block_id})
        if not sensor:
            raise NotFoundException("Block has no sensor connected")
        sensor['id'] = str(sensor['_id'])  
        return Sensor(**sensor)

    

    @staticmethod
    def getSensorByMacAndPin(mac_address: str, pin: int):
        sensor = mongo.db.sensors.find_one({
            "mac_address": mac_address,
            "pin": pin
        })
        if not sensor:
            raise NotFoundException("No sensor found")
        sensor['id'] = str(sensor['_id'])  
        return Sensor(**sensor)

    

    @staticmethod
    def getSensorsByLandId(land_id: str):
        sensors = list(mongo.db.sensors.find({"land_id": land_id}))
        if not sensors:
            raise NotFoundException("The land has no sensors registered")
        for sensor in sensors:
            sensor['id'] = str(sensor['_id'])  
        return [Sensor(**sensor) for sensor in sensors]

    

    @staticmethod
    def registerSensor(ssid: str, data: dict):
        try:
            land = LandService.get_land_by_wifi_ssid(ssid)
            data["land_id"] = land.id
            try:
                existing_sensor = SensorService.getSensorByMacAndPin(
                    data["mac_address"], data["pin"]
                )
                SensorService.updateSensorStatusAndHeartbeat(
                    data["mac_address"], data["pin"], SensorStatus.DISCONNECTED
                )
                return str(existing_sensor.id)

            except NotFoundException:
                data["status"] = SensorStatus.DISCONNECTED.value
                data["last_heartbeat"] = datetime.now()
                sensor = Sensor(**data)
                result = mongo.db.sensors.insert_one(sensor.model_dump(exclude={"id"}))
                sensor_id = str(result.inserted_id)
                LandService.add_sensor_to_land(land.id, sensor_id)
                return sensor_id

        except NotFoundException as e:
            raise NotFoundException(f"Land with ssid : {ssid} is not found")

        except ValidationError as ve:
            raise BadRequestException(f"Invalid sensor data: {ve}")

        except Exception as e:
            raise Exception(f"Error registering sensor: {e}")



    @staticmethod
    def getSensorByStatus(land_id: str, status: SensorStatus):
        sensors = list(mongo.db.sensors.find({"land_id": land_id, "status": status.value}))
        if not sensors:
            raise NotFoundException(f"sensors that have {status.value} status, are not found")
        for sensor in sensors:
            sensor['id'] = str(sensor['_id'])  # Map _id to id
        return [Sensor(**sensor) for sensor in sensors]

    

    @staticmethod
    def updateSensorStatus(mac_address : str , pin : int , status : SensorStatus):
        result = mongo.db.sensors.update_one(
            {"mac_address": mac_address, "pin": pin},
            {"$set": {"status": status.value}}
        )
        if result.matched_count == 0:
            raise NotFoundException("Sensor not found")
        return True
    
    @staticmethod
    def updateHeartBeat(mac_address: str, pin: int):
        # 1. Find the sensor first
        sensor = mongo.db.sensors.find_one({"mac_address": mac_address, "pin": pin})
        if not sensor:
            raise NotFoundException("Sensor not found")

        # 2. Check for block_id presence
        block_id = sensor.get("block_id")
        if block_id and block_id != "" and block_id is not None:
            status = SensorStatus.CONNECTED.value
        else:
            status = SensorStatus.DISCONNECTED.value

        # 3. Update heartbeat and status
        result = mongo.db.sensors.update_one(
            {"mac_address": mac_address, "pin": pin},
            {"$set": {
                "last_heartbeat": datetime.now(),
                "status": status
            }}
        )
        if result.matched_count == 0:
            raise NotFoundException("Sensor not found")

        return True

    @staticmethod
    def updateSensorStatusAndHeartbeat(mac_address: str, pin: int, status: SensorStatus):
        result = mongo.db.sensors.update_one(
            {"mac_address": mac_address, "pin": pin},
            {"$set": {
                "status": status.value,
                "last_heartbeat": datetime.now()
            }}
        )
        if result.matched_count == 0:
            raise NotFoundException("Sensor not found")
        return True

    

        
