from sanic import Request
from sanic.response import HTTPResponse, json as sanicjson
from components.login.Login import Login
from components.repository.DDBRepository import DDBRepository
from components.login.JWTManager import *
from config import config as appconfig

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
    decoded_id_token = decode_google_jwt(tokens['id_token'])
    logger.debug(f"Authenticated: {decoded_id_token}")
    response = sanicjson({"email": decoded_id_token['email'], "jwt": generate_jwt(decoded_id_token)})
    at = generate_access_token(decoded_id_token['email'])
    rt = generate_refresh_tolen(decoded_id_token['email'])
    response.add_cookie(
        "access_token",
        at,
        domain=f"{appconfig.DOMAIN}",
        httponly=True
    )
    response.add_cookie(
        "refresh_token",
        rt,
        domain=f"{appconfig.DOMAIN}",
        httponly=True
    )
    if await Login(DDBRepository()).check_user_is_authorized(decoded_id_token['email']):
        return response
    return HTTPResponse(status=401)

async def refresh_token(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return HTTPResponse(status=401)
    try:
        validate_token(refresh_token, 'rt')
    except:
        return HTTPResponse(status=401)
    new_access_token = generate_access_token("subject")
    return HTTPResponse().add_cookie()
    # get token from Cookie
    # get subject and see if it belongs to the authorized users list
    # validate jwt signature
    # if valid: create a new access token as https only cookie
    # if not valid: return 401
