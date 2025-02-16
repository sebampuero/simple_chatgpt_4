import logging
from sanic import Request
from sanic.response import HTTPResponse
from components.login.JWTManager import *
from config import config as appconfig

logger = logging.getLogger("ChatGPT")

NO_AUTH_NEEDED = [
	f"/{appconfig.SUB_DIRECTORY}/api/login-code", 
	f"/{appconfig.SUB_DIRECTORY}/ws"
]

async def authenticate_requests(request: Request):
	if request.path not in NO_AUTH_NEEDED:
		logger.debug(f"Proceeding to authenticate route: {request.path} because not in {NO_AUTH_NEEDED}")
		token = request.headers.get('Authorization')
		if not token:
			return HTTPResponse(status=401)
		if not validate_jwt(token):
			return HTTPResponse(status=401)
