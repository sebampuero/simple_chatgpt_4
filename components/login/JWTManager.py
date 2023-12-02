import jwt
from jwt import PyJWKClient
import os
import logging

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
