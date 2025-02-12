from sanic import Request
from sanic.response import HTTPResponse, json as sanicjson
from components.login.Login import Login
from components.repository.DDBRepository import DDBRepository
from components.login.JWTManager import JWTManager
from config import config as appconfig
from constants.GoogleServicesConstants import GoogleServicesConstants

import logging
import aiohttp


logger = logging.getLogger("ChatGPT")

async def login_code(request: Request):
    try:
        body = request.json
        auth_code = body.get('code')
    except Exception as e:
        logger.error(f"Error parsing JSON: {e}")
        return HTTPResponse(status=400)
    data = {
        'code': auth_code,
        'client_id': appconfig.GOOGLE_OAUTH_CLIENT_ID,
        'client_secret': appconfig.GOOGLE_OAUTH_CLIENT_SECRET,
        'redirect_uri': 'postmessage',
        'grant_type': 'authorization_code'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(appconfig.OAUTH_TOKEN_URL, data=data) as response:
            tokens = await response.json()
    jwt_manager = JWTManager()
    decoded_id_token = jwt_manager.decode_google_jwt(tokens['id_token'])
    logger.debug(f"Authenticated: {decoded_id_token}")
    if await Login(DDBRepository()).check_user_is_authorized(decoded_id_token['email']):
        return sanicjson({"email": decoded_id_token['email'], "jwt": jwt_manager.generate_jwt(decoded_id_token)})
    return HTTPResponse(status=401)

async def refresh_token(request: Request):
    pass
    # get token from Cookie
    # validate the token
    # if valid: create a new access token as https only cookie
    # if not valid: return 401
