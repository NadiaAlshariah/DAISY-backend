from app.database import mongo
from app.models.User import User
from werkzeug.security import generate_password_hash, check_password_hash
from app.exception.BadRequestException import BadRequestException 
from app.exception.NotFoundException import NotFoundException
from bson import ObjectId


class UserService:
    @staticmethod
    def create_user(username: str, email: str, password: str):
        if UserService.find_by_email(email):
            raise BadRequestException("email already exists")
        
        if UserService.find_by_username(username):
            raise BadRequestException("username already exists")

        hashed_password = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed_password)
            
        result = UserService.save(user)
        return result
    

    @staticmethod
    def change_password(user_id: str, current_password: str, new_password: str):
        try:
            user_object_id = ObjectId(user_id)
        except Exception:
            raise BadRequestException("Invalid user ID format")

        user = mongo.db.users.find_one({"_id": user_object_id})
        if not user:
            raise NotFoundException("User not found")

        if not UserService.verify_password(user["password"], current_password):
            raise BadRequestException("Incorrect current password")

        hashed_new_password = generate_password_hash(new_password)
        mongo.db.users.update_one(
            {"_id": user_object_id},
            {"$set": {"password": hashed_new_password}}
        )
     
     
    @staticmethod
    def save(user: User):
        user_data = {
            "username": user.username,
            "email": user.email,
            "password": user.password, 
        }
        if user.id:
            mongo.db.users.update_one({"_id": user.id}, {"$set": user_data})
        else:
            result = mongo.db.users.insert_one(user_data)
            user._id = result.inserted_id
        return user._id


    @staticmethod
    def find_by_email(email: str) -> User:
        user_data = mongo.db.users.find_one({"email": email})

        if user_data:
            user_data["id"] = str(user_data.pop("_id"))
            return User(**user_data)
        
        return None
    
    
    @staticmethod
    def find_by_username(username: str) -> User:
        user_data = mongo.db.users.find_one({"username": username})
        if user_data:
            user_data["id"] = str(user_data.pop("_id"))
            return User(**user_data)
        
        return None
    
    @staticmethod
    def verify_password(hashedPassword ,password) -> bool:
        return check_password_hash(hashedPassword, password)
    
