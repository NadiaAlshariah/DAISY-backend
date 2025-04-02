from datetime import datetime
from app.database import mongo

class JwtService:
    # mongo will create a document name refresh_tokens when insert one is called for the first time
    @staticmethod
    def add_refresh_token(jti, user_id):
        mongo.db.refresh_tokens.insert_one({
            "jti": jti,  
            "user_id": user_id,
            "created_at": datetime.now(),
            "revoked": False
        })

    @staticmethod
    def revoke_token(jti):
        mongo.db.refresh_tokens.update_one(
            {"jti": jti},
            {"$set": {"revoked": True}}
        )

    @staticmethod
    def is_token_revoked(jti) -> bool:
        token = mongo.db.refresh_tokens.find_one({"jti": jti})
        return token is None or token["revoked"]