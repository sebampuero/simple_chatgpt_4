import logging
from sanic import Request
from sanic.response import HTTPResponse
from components.login.JWTManager import *
from components.login.Login import Login
from sanic import Sanic

logger = logging.getLogger("ChatGPT")

async def authenticate_requests(request: Request):
    app = Sanic.get_app()
    no_auth_needed = [
        f"/{app.config.SUB_DIRECTORY}/api/login-code",
        f"/{app.config.SUB_DIRECTORY}/api/refresh",
    ]
    if request.path not in no_auth_needed:
        logger.debug(
            f"Proceeding to authenticate route: {request.path} because not in {no_auth_needed}"
        )
        token = request.cookies.get("access_token")
        if not token:
            return HTTPResponse(status=401)
        if not validate_token(token, type="at"):
            return HTTPResponse(status=401)
        email = get_subject_access_token(token)
        if not email:
            return HTTPResponse(status=401)
        if not await Login().check_user_is_authorized(email):
            return HTTPResponse(status=401)
