from flask import Blueprint, jsonify, request
from app.services.JwtService import JwtService
from app.services.UserService import UserService
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token, create_refresh_token, decode_token
from app.database import mongo
from werkzeug.exceptions import Conflict, BadRequest

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("No JSON data provided")
        
        username = data["username"]
        email = data["email"]
        password = data["password"]

        if "@" in username:
            raise BadRequest("Username cannot contain '@'")
        
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
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500



@auth_bp.route('/login', methods=['POST'])
def login():
    # changed the input to "email_or_username" and "password"
    data = request.get_json()
    if not data.get("email_or_username") or not data.get("password"):
        return jsonify({"error": "Missing email/username or password"}), 400
    
    email_or_username = data["email_or_username"]
    password = data["password"]

    if "@" in email_or_username:
        user = mongo.db.users.find_one({"email": email_or_username})
    else:
        if "@" in email_or_username:
            return jsonify({"error": "Username cannot contain '@'"}), 400
        user = mongo.db.users.find_one({"username": email_or_username})

    if not user or not UserService.verify_password(user["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    user_id = str(user["_id"])
    access_token = create_access_token(
        identity=user_id,
        additional_claims={
            "role": user.get("role", "user")
        }
    )
    refresh_token = create_refresh_token(identity=user_id)
    refresh_token_data = decode_token(refresh_token)
    refresh_jti = refresh_token_data['jti']
    print(refresh_jti)
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

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    JwtService.revoke_token(get_jwt_identity())
    return jsonify(message="Logged out"), 200
    