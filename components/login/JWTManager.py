import jwt
from jwt import PyJWKClient
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class JWTManager:

    GOOGLE_PUBLIC_KEY_URL = "https://www.googleapis.com/oauth2/v3/certs"

    def decode_google_jwt(self, token: str):
        logger.debug(f"Trying to decode google token {token}")
        jwks_client = PyJWKClient(self.GOOGLE_PUBLIC_KEY_URL)
        data = jwt.decode(
            token,
            jwks_client.get_signing_key_from_jwt(token).key,
            algorithms=["RS256"],
            audience=os.getenv("CLIENT_ID")
        )
        logger.debug(f"Decoded to {data}")
        return data
    
    def generate_jwt(self, id_token: dict):
        secret = os.getenv("JWT_SECRET")
        exp = int(datetime.now().timestamp()) + 86400 * 7
        encoded = jwt.encode({"authenticated": True, "email": id_token['email'], "exp": exp}, secret, algorithm="HS256")
        return encoded
    
    def validate_jwt(self, jwt_str: str):
        secret = os.getenv("JWT_SECRET")
        try:
            decoded = jwt.decode(jwt_str, secret, algorithms="HS256")
            if int(datetime.now().timestamp()) > decoded['exp']:
                logger.info("Token expired.")
                return False
            logger.info(f"Valid token: {decoded}")
            return True
        except jwt.exceptions.InvalidSignatureError:
            logger.info(f"JWT token was tampered with, signature is invalid. {jwt_str}")
            return False
        except KeyError:
            logger.info("Expiration was not found in JWT")
            return False
        except:
            logger.error("General error while validating jwt", exc_info=True)
            return False        

