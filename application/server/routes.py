from sanic import Websocket, Request
from sanic.response import HTTPResponse, file
from sanic.response import json as sanicjson
from components.login.Login import Login
from components.llm.GPT4 import GPT4
from components.llm.Gemini import Gemini
from components.llm.Mistral import Mistral
from components.repository.DDBRepository import DDBRepository
from components.login.JWTManager import JWTManager
from components.chat.ChatState import ChatState
from components.elasticsearch.ElasticClient import ElasticClient
import logging, json
from datetime import datetime
from functools import wraps
import aiohttp
import os
# TODO: refactor into oop
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
async def get_chats_for_user(request: Request):
    email = request.args.get('email')
    last_eval_key = request.args.get('last_eval_key') 
    try:
        limit = int(request.args.get('limit'))
    except:
        return HTTPResponse(status=400)
    if last_eval_key:
        try:
            last_eval_key = json.loads(last_eval_key)
        except:
            return HTTPResponse(status=400)
    if email.strip() == '':
        return HTTPResponse(status=400)
    results = await DDBRepository().get_chats_by_email_paginated(email, last_eval_key, limit)
    chats = results['chats']
    last_eval_key = results['last_eval_key']
    return sanicjson({"chats": chats, "lastEvalKey": last_eval_key})

@authorize()
async def search_for_chat(request: Request):
    body = request.json
    keywords = body.get('keywords')
    email_address = body.get('email_address')
    chats = ElasticClient().search_chats_by_keyword(keyword=keywords, email_address=email_address)
    return sanicjson({"chats": chats})

@authorize()
async def load_new_chat(request: Request, id: str, timestamp: str, new_socket_id: str, old_socket_id: str):
    if id is None or id.strip() == '':
        return HTTPResponse(status=400)
    chat_data = await DDBRepository().get_chat_by_id(id, int(timestamp))
    if chat_data is None:
        return HTTPResponse(status=404)
    chat_state = ChatState.get_instance()
    chat_state.set_messages_with_ts(chat_data['messages'], new_socket_id, int(timestamp))
    chat_state.remove_ws(old_socket_id)
    return sanicjson({"body": chat_data})

@authorize()
async def set_model(request: Request, socket_id: str):
    body = request.json
    model = body.get('model')
    chat_state = ChatState.get_instance()
    chat_state.set_language_model(model, socket_id)
    return HTTPResponse(status=200)

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

language_models = {
    "GPT4": GPT4(),
    "Gemini": Gemini(),
    "Mistral": Mistral()
}

async def chat(request: Request, ws: Websocket):
    """
    Main websocket endpoint
    """
    client_ip = request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
    token = request.args.get('token')
    if token:
        if not JWTManager().validate_jwt(token):
            await ws.close()
            return
    else:
        await ws.close()
        return
    socket_id = str(id(ws))
    user_email = ""
    chat_id = ""
    logger.info(f"Client connected via WS: {client_ip} and socket_id {socket_id}")
    await ws.send(json.dumps({"socket_id": socket_id, "type": "INIT"}))
    chat_state = ChatState.get_instance()
    chat_state.set_messages_with_ts([], socket_id, int(datetime.now().timestamp()))

    async def close_connection():
        await DDBRepository().store_chat(chat_state.get_messages_with_ts(socket_id), user_email, chat_id)
        chat_state.remove_ws(socket_id)
        await ws.close()

    while True:
        message_timestamp = datetime.timestamp(datetime.now())
        try:
            input_raw = await ws.recv()
        except:
            logger.error(f"Unexpected exception, most probably {client_ip} closed the websocket connection",exc_info=True)
            await close_connection()
            break
        if not input_raw or "email" not in input_raw:
            await close_connection()
            break
        try:
            input_json = json.loads(input_raw)
        except json.JSONDecodeError:
            logger.debug(f"Client IP {client_ip} sent unsupported command")
            await ws.close()
            break
        user_email = input_json['email']
        chat_id = input_json['chat_id']
        chat_state.append_message({
            "role": "user",
            "image": input_json['image'],
            "content": input_json['msg']
        }, socket_id)
        try:
            language_model = chat_state.get_language_model(socket_id)
            response_generator = await language_models[language_model].prompt(chat_state.get_messages_with_ts(socket_id)['messages'])
            assistant_msg = await language_models[language_model].process_response(response_generator, ws, int(message_timestamp))
            await ws.send(json.dumps({"content": "END", "timestamp": int(message_timestamp), "type": "CONTENT"}))
            chat_state.append_message({
                "role": "assistant",
                "content": assistant_msg,
                "language_model": chat_state.get_language_model(socket_id)
            }, socket_id)
        except Exception as e:
            logger.error(str(e), exc_info=True)
            await DDBRepository().store_chat(chat_state.get_messages_with_ts(socket_id), user_email, chat_id)
            await ws.send(json.dumps({"content": str(e), "timestamp": int(message_timestamp), "type": "CONTENT"}))
    
