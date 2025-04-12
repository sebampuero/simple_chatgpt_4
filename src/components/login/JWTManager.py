import jwt
from jwt import PyJWKClient
import logging
from datetime import datetime, timedelta
from sanic import Sanic

logger = logging.getLogger("ChatGPT")


def decode_google_jwt(token: str):
    app = Sanic.get_app()
    logger.debug(f"Trying to decode google token {token}")
    jwks_client = PyJWKClient(app.config.PUBLIC_CERTS_URL)
    data = jwt.decode(
        token,
        jwks_client.get_signing_key_from_jwt(token).key,
        algorithms=["RS256"],
        audience=app.config.GOOGLE_OAUTH_CLIENT_ID,
    )
    logger.debug(f"Decoded to {data}")
    return data


def generate_access_token(subject: str, expires_delta: int = None) -> str:
    app = Sanic.get_app()
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes=float(app.config.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, app.config.ACCESS_TOKEN_SECRET, app.config.JWT_ALGORITHM
    )
    return encoded_jwt


def generate_refresh_token(subject: str, expires_delta: int = None) -> str:
    app = Sanic.get_app()
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes=float(app.config.REFRESH_TOKEN_EXPIRE_MINUTES)
        )

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, app.config.REFRESH_TOKEN_SECRET, app.config.JWT_ALGORITHM
    )
    return encoded_jwt


def validate_token(
    token: str, type: str
) -> bool: 
    app = Sanic.get_app()
    if type == "at":  # access_token
        secret = app.config.ACCESS_TOKEN_SECRET
    elif type == "rt":  # refresh token
        secret = app.config.REFRESH_TOKEN_SECRET
    else:
        logger.error("Bad token passed, using access token secret.")
        secret = app.config.ACCESS_TOKEN_SECRET
    try:
        jwt.decode(token, secret, algorithms=app.config.JWT_ALGORITHM)
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


def validate_jwt(jwt_str: str):
    app = Sanic.get_app()
    secret = app.config.JWT_SECRET
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


def get_subject_refresh_token(token: str) -> str | None:
    app = Sanic.get_app()
    try:
        payload = jwt.decode(
            token, app.config.REFRESH_TOKEN_SECRET, algorithms=[app.config.JWT_ALGORITHM]
        )
        subject: str = payload.get("sub")
        if not subject:
            return None
        return subject
    except jwt.ExpiredSignatureError:
        logger.error(f"Token expired for subject {subject}", exc_info=True)
        return None
    except jwt.InvalidTokenError:
        logger.error(f"Token invalid for subject {subject}", exc_info=True)
        return None
    except jwt.PyJWTError:
        logger.êrror(f"General error for subject {subject}", exc_info=True)
        return None


def get_subject_access_token(token: str) -> str | None:
    app = Sanic.get_app()
    try:
        payload = jwt.decode(
            token, app.config.ACCESS_TOKEN_SECRET, algorithms=[app.config.JWT_ALGORITHM]
        )
        subject: str = payload.get("sub")
        if not subject:
            return None
        return subject
    except jwt.ExpiredSignatureError:
        logger.error(f"Token expired for subject {subject}", exc_info=True)
        return None
    except jwt.InvalidTokenError:
        logger.error(f"Token invalid for subject {subject}", exc_info=True)
        return None
    except jwt.PyJWTError:
        logger.êrror(f"General error for subject {subject}", exc_info=True)
        return None
