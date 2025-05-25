from bson import ObjectId
from flask import Blueprint, jsonify, request
from app.services.JwtService import JwtService
from app.services.UserService import UserService
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token, decode_token
from app.database import mongo
from app.exception.BadRequestException import BadRequestException 
from app.exception.NotFoundException import NotFoundException

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data["username"]
    email = data["email"]
    password = data["password"]
    
    if not all([username, email, password]):
        raise BadRequestException("Missing required fields (username, email, password)")
    
    user_id = UserService.create_user(username, email , password)
    access_token = create_access_token(
    identity=str(user_id),
    additional_claims={
        "username": username,
        "role": "user"
        }
    )
    refresh_token = create_refresh_token(identity=str(user_id))
    refresh_payload = decode_token(refresh_token)
    JwtService.add_refresh_token(
        jti=refresh_payload['jti'],
        user_id=str(user_id)
    )
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """"changed the input to 'email_or_username' and 'password'"""

    data = request.get_json()
    if not data.get("email_or_username") or not data.get("password"):
        raise BadRequestException({"error": "Missing email/username or password"})
    
    email_or_username = data["email_or_username"]
    password = data["password"]

    if "@" in email_or_username:
        user = mongo.db.users.find_one({"email": email_or_username})
    else:
        user = mongo.db.users.find_one({"username": email_or_username})

    if not user or not UserService.verify_password(user["password"], password):
        raise BadRequestException("Incorrect email / username or password. Please try again.")

    user_id = str(user["_id"])
    access_token = create_access_token(
        identity=user_id,
        additional_claims={
            "username": user.get("username"),
            "role": user.get("role", "user")
        }
    )
    refresh_token = create_refresh_token(identity=user_id)
    refresh_token_data = decode_token(refresh_token)
    refresh_jti = refresh_token_data['jti']
    JwtService.add_refresh_token(jti=refresh_jti, user_id=user_id)
    return jsonify(
            access_token=access_token,
            refresh_token=refresh_token), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    
    JwtService.revoke_token(current_user)
    new_access_token = create_access_token(identity=current_user)
    new_refresh_token = create_refresh_token(identity=current_user)
    
    new_refresh_payload = decode_token(new_refresh_token)
    JwtService.add_refresh_token(
        jti=new_refresh_payload['jti'],
        user_id=current_user
    )
    return jsonify(
        access_token=new_access_token,
        refresh_token=new_refresh_token
    ), 200 


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    data = request.get_json()
    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not current_password or not new_password:
        raise BadRequestException("Current and new passwords are required")

    UserService.change_password(user_id, current_password, new_password)

    return jsonify(message="Password updated successfully"), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    JwtService.revoke_token(get_jwt_identity())
    return jsonify(message="Logged out"), 200
    