from sanic import Websocket, Request
from sanic.response import HTTPResponse, file
from sanic.response import json as sanicjson
from components.login.Login import Login
from components.gpt_4.GPT4 import GPT4
from components.repository.DDBRepository import DDBRepository
from components.login.JWTManager import JWTManager
import logging, json, openai
from datetime import datetime
from functools import wraps
import aiohttp
import os

logger = logging.getLogger(__name__)

def authorize():
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return HTTPResponse(status=401)
            if not JWTManager().validate_jwt(token):
                return HTTPResponse(status=401)
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

async def serve_index(request: Request):
    return await file("static/index.html")

async def serve_static(request: Request, filename):
    return await file(f"static/{filename}")

@authorize()
async def get_chats_for_user(request: Request, email: str):
    if email.strip() == '':
        return HTTPResponse(status=400)
    chats = await DDBRepository().get_chats_by_email(email)
    return sanicjson({"body": chats})

@authorize()
async def load_new_chat(request: Request, id: str, timestamp: str, socket_id: str):
    if id is None or id.strip() == '':
        return HTTPResponse(status=400)
    chat_data = await DDBRepository().get_chat_by_id(id, int(timestamp))
    if chat_data is None:
        return HTTPResponse(status=404)
    gpt4 = GPT4.getInstance()
    gpt4.set_messages_info(socket_id, int(timestamp), chat_data['messages'])
    return sanicjson({"body": chat_data})

@authorize()
async def delete_chat(request: Request, id: str, timestamp: str):
    if id.strip() == '':
        return HTTPResponse(status=400)
    await DDBRepository().delete_chat_by_id(id, int(timestamp))
    return HTTPResponse(status=204)

async def login_code(request: Request):
    try:
        body = request.json
        auth_code = body.get('code')
    except Exception as e:
        logger.error(f"Error parsing JSON: {e}")
        return HTTPResponse(status=400)
    data = {
        'code': auth_code,
        'client_id': os.getenv("CLIENT_ID"),
        'client_secret': os.getenv("CLIENT_SECRET"),
        'redirect_uri': 'postmessage',
        'grant_type': 'authorization_code'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post('https://oauth2.googleapis.com/token', data=data) as response: #TODO: remove hardcoded token URL
            tokens = await response.json()
    jwt_manager = JWTManager()
    decoded_id_token = jwt_manager.decode_google_jwt(tokens['id_token'])
    logger.debug(f"Authenticated: {decoded_id_token}")
    if await Login(DDBRepository()).check_user_is_authorized(decoded_id_token['email']):
        return sanicjson({"email": decoded_id_token['email'], "jwt": jwt_manager.generate_jwt(decoded_id_token)})
    return HTTPResponse(status=401)

async def chat(request: Request, ws: Websocket):
    """
    Main websocket endpoint
    """
    client_ip = request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
    token = request.args.get('token')
    if token:
        if not JWTManager().validate_jwt(token):
            await ws.close()
    else:
        await ws.close()
    socket_id = str(id(ws))
    user_email = ""
    chat_id = ""
    logger.info(f"Client connected via WS: {client_ip} and socket_id {socket_id}")
    await ws.send(json.dumps({"socket_id": socket_id, "type": "INIT"}))
    while True:
        message_timestamp = datetime.timestamp(datetime.now())
        gpt4 = GPT4.getInstance()
        try:
            input_raw = await ws.recv()
        except:
            logger.error(f"Unexpected exception, most probably {client_ip} closed the websocket connection",exc_info=True)
            await DDBRepository().store_chat(gpt4.get_messages_info(socket_id), user_email, chat_id)
            gpt4.remove_socket_id(socket_id)
            break
        if not input_raw:
            logger.info(f"{client_ip} closed the connection")
            await DDBRepository().store_chat(gpt4.get_messages_info(socket_id), user_email, chat_id)
            gpt4.remove_socket_id(socket_id)
            break
        try:
            input_json = json.loads(input_raw)
        except json.JSONDecodeError:
            logger.debug(f"Client IP {client_ip} sent unsupported command")
            await ws.close()
            break
        if "email" not in input_json:
            await ws.close()
            break
        logger.debug("Input JSON from WS: " + json.dumps(input_json, indent=4))
        user_email = input_json['email']
        chat_id = input_json['chat_id']
        response_generator = await gpt4.prompt(socket_id, input_json)
        assistant_msg = ""
        try:
            async for response_chunk in response_generator:
                delta = response_chunk["choices"][0]["delta"]
                if "content" in delta:
                    await ws.send(json.dumps({"content": delta["content"], "timestamp": int(message_timestamp), "type": "CONTENT"}))
                    assistant_msg += delta["content"]
            await ws.send(json.dumps({"content": "END", "timestamp": int(message_timestamp), "type": "CONTENT"}))
            gpt4.append_to_msg_history_as_assistant(socket_id, assistant_msg)
        except openai.error.RateLimitError:
            logger.error(f"Rate limit exceeded", exc_info=True)
            await ws.send(json.dumps({"content": "Usage limit exceeded", "timestamp": int(message_timestamp), "type": "CONTENT"}))
        except openai.error.APIError:
            logger.error(exc_info=True)
            await ws.send(json.dumps({"content": "GPT4 had an error generating response for the prompt", "timestamp": int(message_timestamp), "type": "CONTENT"}))
        except:
            logger.error(exc_info=True)
            await  ws.send(json.dumps({"content": "General error, try again later", "timestamp": int(message_timestamp), "type": "CONTENT"}))
    