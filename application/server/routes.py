from sanic import Websocket, Request
from sanic.response import HTTPResponse, file
from sanic.response import json as sanicjson
from components.login.Login import Login
from components.gpt_4.GPT4 import GPT4
from components.repository.DDBRepository import DDBRepository
import logging, json, openai
from datetime import datetime

CHANGING_CHAT = "chat_change"

logger = logging.getLogger(__name__)
# Register routes

async def serve_index(request: Request):
    return await file("static/index.html")

async def serve_static(request: Request, filename):
    return await file(f"static/{filename}")

async def get_chats_for_user(request: Request, email: str):
    if email.strip() == '':
        return HTTPResponse(status=400)
    chats = await DDBRepository().get_chats_by_email(email)
    return sanicjson({"body": chats})

async def load_new_chat(request: Request, id: str, socket_id: str):
    if id is None or id.strip() == '':
        return HTTPResponse(status=400)
    chat_data = await DDBRepository().get_chat_by_id(id)
    if chat_data is None:
        return HTTPResponse(status=404)
    gpt4 = GPT4.getInstance()
    gpt4.set_messages(socket_id, chat_data['messages'])
    return sanicjson({"body": chat_data})

async def delete_chat(request: Request, id: str):
    if id.strip() == '':
        return HTTPResponse(status=400)
    await DDBRepository().delete_chat_by_id(id)
    return HTTPResponse(status=204)

async def login(request: Request):
    """
    Checks if user's email is authenticated
    """
    try:
        # Assuming the request body is in JSON format
        body = request.json
        email = body.get('email')
    except Exception as e:
        logger.error(f"Error parsing JSON: {e}")
        return HTTPResponse(status=400)
    login_supp = Login(DDBRepository())
    if await login_supp.check_user_is_authorized(email):
        return HTTPResponse(status=200)
    logger.info(f"Bad email entered by {request.headers.get('X-Forwarded-For', '').split(',')[0].strip()}: {email}")
    return HTTPResponse(status=401)

async def chat(request: Request, ws: Websocket):
    """
    Main websocket endpoint
    """ #TODO: dismantle in separate methods
    client_ip = request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
    socket_id = str(id(ws))
    user_email = ""
    chat_id = ""
    logger.info(f"Client connected via WS: {client_ip} and socket_id {socket_id}")
    await ws.send(json.dumps({"socket_id": socket_id, "type": "INIT"}))
    while True:
        dt = datetime.now()
        ts = datetime.timestamp(dt)
        gpt4 = GPT4.getInstance()
        try:
            input_raw = await ws.recv()
        except:
            logger.error(f"Unexpected exception, most probably {client_ip} closed the websocket connection",exc_info=True)
            await DDBRepository().store_chat(gpt4.get_messages(socket_id), user_email, chat_id)
            gpt4.remove_socket_id(socket_id)
            break
        if not input_raw:
            logger.info(f"{client_ip} closed the connection")
            await DDBRepository().store_chat(gpt4.get_messages(socket_id), user_email, chat_id)
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
                    await ws.send(json.dumps({"content": delta["content"], "timestamp": int(ts), "type": "CONTENT"}))
                    assistant_msg += delta["content"]
            await ws.send(json.dumps({"content": "END", "timestamp": int(ts), "type": "CONTENT"}))
            gpt4.append_to_msg_history_as_assistant(socket_id, assistant_msg)
        except openai.error.RateLimitError:
            logger.error(f"Rate limit exceeded", exc_info=True)
            await ws.send("Se alcanzo el limite de $8 mensuales para uso de GPT-4")
        except openai.error.APIError:
            logger.error(exc_info=True)
            await ws.send("Hubo un error con al API de GPT4")
        except openai.error.APIConnectionError:
            logger.error(exc_info=True)
            await ws.send("No se pudo conectar con GPT4, vuelve a intentar mas tarde")
        except:
            logger.error(exc_info=True)
            await  ws.send("Error, vuelve a intentar mas tarde")