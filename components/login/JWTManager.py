import jwt
from jwt import PyJWKClient
import os
import logging
from datetime import datetime
from config import config as appconfig

logger = logging.getLogger("ChatGPT")

class JWTManager:

    PUBLIC_CERTS_URL = appconfig.PUBLIC_CERTS_URL
    JWT_ALGORITHM = appconfig.JWT_ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = appconfig.ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE_MINUTES = appconfig.REFRESH_TOKEN_EXPIRE_MINUTES
    ACCESS_TOKEN_SECRET = appconfig.ACCESS_TOKEN_SECRET
    REFRESH_TOKEN_SECRET = appconfig.REFRESH_TOKEN_SECRET

    def decode_google_jwt(self, token: str):
        logger.debug(f"Trying to decode google token {token}")
        jwks_client = PyJWKClient(self.PUBLIC_CERTS_URL)
        data = jwt.decode(
            token,
            jwks_client.get_signing_key_from_jwt(token).key,
            algorithms=["RS256"],
            audience=appconfig.GOOGLE_OAUTH_CLIENT_ID
        )
        logger.debug(f"Decoded to {data}")
        return data
    
    def generate_jwt(self, id_token: dict):
        secret = self.ACCESS_TOKEN_SECRET
        exp = int(datetime.now().timestamp()) + 86400 * 7
        encoded = jwt.encode({"authenticated": True, "email": id_token['email'], "exp": exp}, secret, algorithm=self.JWT_ALGORITHM)
        return encoded

    def generate_access_token(self, subject: str, expires_delta: int = None) -> str:
        if expires_delta is not None:
            expires_delta = datetime.utcnow() + expires_delta
        else:
            expires_delta = datetime.utcnow() + timedelta(minutes=float(self.ACCESS_TOKEN_EXPIRE_MINUTES))

        to_encode = {"exp": expires_delta, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, self.ACCESS_TOKEN_SECRET, self.JWT_ALGORITHM)
        return encoded_jwt

    def generate_refresh_tolen(self, subject: str, expires_delta: int = None) -> str:
        if expires_delta is not None:
            expires_delta = datetime.utcnow() + expires_delta
        else:
            expires_delta = datetime.utcnow() + timedelta(minutes=float(self.REFRESH_TOKEN_EXPIRE_MINUTES))

        to_encode = {"exp": expires_delta, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, self.REFRESH_TOKEN_SECRET, self.JWT_ALGORITHM)
        return encoded_jwt
    
    def validate_token(self, token: str, type: str) -> bool: #TODO: add Annotation for type field description or use constants
        if type == 'at': # access_token
            secret = self.ACCESS_TOKEN_SECRET
        elif type == 'rt': # refresh token
            secret = self.REFRESH_TOKEN_SECRET
        else:
            logger.error("Bad token passed, using access token secret.")
            secret = self.ACCESS_TOKEN_SECRET
        try:
            jwt.decode(token, secret, algorithms=self.JWT_ALGORITHM)
            return True
        except jwt.exceptions.ExpiredSignatureError:
            logger.info("Expired.", exc_info=True)
            return False
        except jwt.exceptions.InvalidSignatureError:
            logger.info(f"JWT token was tampered with, signature is invalid. {token}")
            return False
        except KeyError:
            logger.info("Expiration was not found in JWT")
            return False
        except:
            logger.error("General error while validating jwt", exc_info=True)
            return False    


    def validate_jwt(self, jwt_str: str):
        secret = appconfig.MISTRAL_API_KEY
        try:
            jwt.decode(jwt_str, secret, algorithms="HS256")
            return True
        except jwt.exceptions.ExpiredSignatureError:
            logger.info("Expired.", exc_info=True)
            return False
        except jwt.exceptions.InvalidSignatureError:
            logger.info(f"JWT token was tampered with, signature is invalid. {jwt_str}")
            return False
        except KeyError:
            logger.info("Expiration was not found in JWT")
            return False
        except:
            logger.error("General error while validating jwt", exc_info=True)
            return False        

