from sanic import Request
from sanic.response import HTTPResponse, json as sanicjson
from components.login.Login import Login
from components.login.JWTManager import (
    get_subject_access_token,
    generate_access_token,
    generate_refresh_token,
    get_subject_refresh_token,
    decode_google_jwt,
    validate_token,
)
from sanic import Sanic
from datetime import timedelta

import logging
import aiohttp



logger = logging.getLogger("ChatGPT")



async def login_code(request: Request):
    app = Sanic.get_app()
    try:
        body = request.json
        auth_code = body.get("code")
    except Exception as e:
        logger.error(f"Error parsing JSON: {e}")
        return HTTPResponse(status=400)
    data = {
        "code": auth_code,
        "client_id": app.config.GOOGLE_OAUTH_CLIENT_ID,
        "client_secret": app.config.GOOGLE_OAUTH_CLIENT_SECRET,
        "redirect_uri": "postmessage",
        "grant_type": "authorization_code",
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(app.config.OAUTH_TOKEN_URL, data=data) as response:
            tokens = await response.json()
    decoded_id_token = decode_google_jwt(tokens["id_token"])
    logger.debug(f"Authenticated: {decoded_id_token}")
    response = sanicjson({"email": decoded_id_token["email"]})
    at = generate_access_token(decoded_id_token["email"])
    rt = generate_refresh_token(decoded_id_token["email"])
    response.add_cookie(
        "access_token",
        at,
        domain=f"{app.config.DOMAIN}",
        httponly=True,
        max_age=app.config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.add_cookie(
        "refresh_token",
        rt,
        domain=f"{app.config.DOMAIN}",
        httponly=True,
        max_age=app.config.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )
    if await Login().check_user_is_authorized(decoded_id_token["email"]):
        return response
    return HTTPResponse(status=401)


async def refresh_token(request: Request):
    app = Sanic.get_app()
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        return HTTPResponse(status=401)
    if not validate_token(refresh_token, "rt"):
        return HTTPResponse(status=401)

    subject = get_subject_refresh_token(refresh_token)
    if not subject:
        return HTTPResponse(status=401)
    if not await Login().check_user_is_authorized(subject):
        return HTTPResponse(status=401)

    new_access_token = generate_access_token(
        subject,
        expires_delta=timedelta(
            minutes=float(app.config.NEW_ACCESS_TOKEN_EXPIRE_MINUTES)
        ),
    )

    response = HTTPResponse()
    response.add_cookie(
        "access_token",
        new_access_token,
        domain=f"{app.config.DOMAIN}",
        httponly=True,
        max_age=app.config.NEW_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response


async def get_authorized_email(request: Request):
    access_token = request.cookies.get("access_token")
    email = get_subject_access_token(access_token)
    if email:
        return sanicjson({"email": email})
    else:
        return HTTPResponse(status=401)
