from app.database import mongo
from app.models.User import User
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo.errors import DuplicateKeyError
from werkzeug.exceptions import Conflict

class UserService:
    @staticmethod
    def create_user(username: str, email: str, password: str, role: str = "user"):
        try:
            if UserService.find_by_email(email) or UserService.find_by_username(username):
                raise Conflict("Email or username already exists")

            hashed_password = generate_password_hash(password)
            user = User(username, email, hashed_password)
            
            result = UserService.save(user)
            return result

        except DuplicateKeyError:
            raise Conflict("Email or username already exists")
     
    @staticmethod
    def save(user: User):
        user_data = {
            "username": user.username,
            "email": user.email,
            "password": user.password_hash, 
            "role": user.role,
            "created_at": user.created_at
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
        return User(user_data) if user_data else None
    
    
    @staticmethod
    def find_by_username(username: str) -> User:
        user_data = mongo.db.users.find_one({"username": username})
        return User(user_data) if user_data else None
    
    @staticmethod
    def verify_password(hashedPassword ,password) -> bool:
        return check_password_hash(hashedPassword, password)
    
