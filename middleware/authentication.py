import logging
from sanic import Request
from sanic.response import HTTPResponse
from components.login.JWTManager import *
from components.login.Login import Login
from config import config as appconfig

logger = logging.getLogger("ChatGPT")

NO_AUTH_NEEDED = [
	f"/{appconfig.SUB_DIRECTORY}/api/login-code",
	f"/{appconfig.SUB_DIRECTORY}/api/refresh",
	f"/{appconfig.SUB_DIRECTORY}/ws"
]


async def authenticate_requests(request: Request):
	if request.path not in NO_AUTH_NEEDED:
		logger.debug(f"Proceeding to authenticate route: {request.path} because not in {NO_AUTH_NEEDED}")
		token = request.cookies.get('access_token')
		if not token:
			return HTTPResponse(status=401)
		if not validate_token(token, type='at'):
			return HTTPResponse(status=401)
		email = get_subject_access_token(token)
		if not email:
			return HTTPResponse(status=401)
		if not await Login().check_user_is_authorized(email):
			return HTTPResponse(status=401)



