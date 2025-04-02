from flask import Blueprint, jsonify, request
from app.models import User
from app.services import JwtService, UserService
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token, create_refresh_token
from app.database import mongo
from pymongo.errors import DuplicateKeyError
from werkzeug.exceptions import Conflict, BadRequest

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', method=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("No JSON data provided")
        
        username = data["username"]
        email = data["email"]
        password = data["password"]

        if not all([username, email, password]):
            raise BadRequest("Missing required fields (username, email, password)")
        
        user_id = UserService.create_user(username, email , password)
        return jsonify({
                "message": "User registered successfully",
                "user_id": str(user_id)  
            }), 201
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Conflict as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500



@auth_bp.route('/login', methods=['POST'])
@jwt_required()
def login():
    data = request.get_json()
    user = mongo.db.users.find_one({"email": data["email"]})
    if not user or not UserService.verify_password(user["password"], data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401
    
    access_token = create_access_token(identity={
            "id": str(user["_id"]),
            "role": user.get("role", "user")
    })
    refresh_token = create_refresh_token(identity={
            "id": str(user["_id"])
    })
    JwtService.add_refresh_token(jti=get_jwt()["jti"], user_id=str(user["_id"]))
    return jsonify(
            access_token=access_token,
            refresh_token=refresh_token), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    
    JwtService.revoke_token(get_jwt()["jti"])
    new_access_token = create_access_token(identity=current_user)
    new_refresh_token = create_refresh_token(identity=current_user)
    JwtService.add_refresh_token(
        jti=get_jwt()["jti"],
        user_id=current_user["id"]
    )
    return jsonify(
        access_token=new_access_token,
        refresh_token=new_refresh_token
    ), 200 

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    JwtService.revoke_token(get_jwt()["jti"])
    return jsonify(message="Logged out"), 200
    