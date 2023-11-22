from sanic import redirect, Websocket, Request, Sanic
from sanic.response import html, json, HTTPResponse, file
from jinja2 import Template
from components.login.Login import Login
from components.gpt_4.GPT4 import GPT4
from components.chat_code_repository.CodeUseSupport import CodeUseSupport
import logging, os, json, openai
from datetime import datetime

logger = logging.getLogger(__name__)
# Register routes

async def serve_index(request):
    return await file("static/index.html")

async def serve_static(request, filename):
    return await file(f"static/{filename}")

async def passwd_code(request: Request):
    """
    Checks if password code is correct and redirects to chat page if so
    """
    try:
        # Assuming the request body is in JSON format
        body = request.json
        code = body.get('code')
    except Exception as e:
        logger.error(f"Error parsing JSON: {e}")
        return HTTPResponse(status=400)
    login_supp = Login()
    if login_supp.check_code_is_correct(code):
        return HTTPResponse(status=200)
    logger.info(f"Bad code entered by {request.headers.get('X-Forwarded-For', '').split(',')[0].strip()}: {code}")
    return HTTPResponse(status=401)

async def chat(request: Request, ws: Websocket):
    """
    Main websocket endpoint
    """
    client_ip = request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
    socket_id = str(id(ws))
    logger.info(f"Client connected via WS: {client_ip} and socket_id {socket_id}")
    while True:
        dt = datetime.now()
        ts = datetime.timestamp(dt)
        gpt4 = GPT4.getInstance()
        code_use_support = CodeUseSupport.getInstance()
        try:
            input_raw = await ws.recv()
        except:
            logger.error(f"Unexpected exception, most probably {client_ip} closed the websocket connection",exc_info=True)
            gpt4.remove_socket_id(socket_id)
            break
        if not input_raw:
            logger.info(f"{client_ip} closed the connection")
            gpt4.remove_socket_id(socket_id)
            break
        try:
            input_json = json.loads(input_raw)
        except json.JSONDecodeError:
            await ws.send("Error")
            logger.debug(f"Client IP {client_ip} did send bad WS packet {input_raw}")
            await ws.close()
            break
        if "code" not in input_json:
            await ws.close()
            break
        code_use_support.update_chat_code_date_if_needed(input_json["code"])
        if code_use_support.max_use_reached(input_json["code"]):
            await ws.send(json.dumps({"content": "Max use reached.", "timestamp": int(ts)}))
            continue
        logger.debug(input_json)
        code_use_support.incr_code_use_count(input_json["code"])
        response_generator = await gpt4.prompt(socket_id, input_json)
        assistant_msg = ""
        try:
            async for response_chunk in response_generator:
                delta = response_chunk["choices"][0]["delta"]
                if "content" in delta:
                    await ws.send(json.dumps({"content": delta["content"], "timestamp": int(ts)}))
                    assistant_msg += delta["content"]
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