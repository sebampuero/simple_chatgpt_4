from sanic import redirect, Websocket, Request, Sanic
from sanic.response import html
from jinja2 import Template
from components.login.Login import Login
from components.gpt_4.GPT4 import GPT4
from components.chat_code_repository.CodeUseSupport import CodeUseSupport
import logging, os, json, openai

logger = logging.getLogger(__name__)
# Register routes

async def index(request: Request):
    """
    Returns main page
    """
    err = request.args["error"][0] if "error" in request.args else "No"
    app = Sanic.get_app("chatgpt4")
    html_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../static/index.html'))
    with open(html_file_path, 'r') as f:
        html_content = Template(f.read())
    context = {
        "subdirectory": app.ctx.sub_directory,
        "error": err
    }
    return html(html_content.render(context))

async def passwd_code(request: Request):
    """
    Checks if password code is correct and redirects to chat page if so
    """
    # get code, check its valid, and then redirect to chat, if not valid, redirect to index
    app = Sanic.get_app("chatgpt4")
    body = request.form
    code = body.get('password-code')
    login_supp = Login()
    if login_supp.check_code_is_correct(code):
        return redirect(app.url_for("chat_page", code=code))
    logger.info(f"Bad code entered by {request.headers.get('X-Forwarded-For', '').split(',')[0].strip()}: {code}")
    url = app.url_for("index", error="Yes")
    return redirect(url)


async def chat_page(request: Request, code: str):
    """
    Serves the GPT-4 chat app in case the correct code is given. If not, request is redirected to <passwd_code>
    """
    login_supp = Login()
    app = Sanic.get_app("chatgpt4")
    if login_supp.check_code_is_correct(code):
        html_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../static/chat.html'))
        with open(html_file_path, 'r') as f:
            html_content = Template(f.read())
        context = {
            "connection_code": code,
            "ws_connection": app.ctx.ws_connection
        }
        return html(html_content.render(context))
    logger.debug("Redirecting to Index because of bad code")
    return redirect(app.url_for("index"))

async def chat(request: Request, ws: Websocket):
    """
    Main websocket endpoint
    """
    client_ip = request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
    socket_id = str(id(ws))
    logger.info(f"Client connected via WS: {client_ip} and socket_id {socket_id}")
    while True:
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
            input = json.loads(input_raw)
        except json.JSONDecodeError:
            await ws.send("Error")
            logger.debug(f"Client IP {client_ip} did send bad WS packet {input_raw}")
            await ws.close()
            break
        if "code" not in input:
            await ws.close()
            break
        if input["msg"] == "RESET":
            gpt4.reset_history(socket_id)
            await ws.send("Historial de mensajes vaciado")
            await ws.send("END")
            continue
        code_use_support.update_chat_code_date_if_needed(input["code"])
        if code_use_support.max_use_reached(input["code"]):
            await ws.send("Uso maximo por hoy alcanzado")
            await ws.send("END")
            continue
        code_use_support.incr_code_use_count(input["code"])
        response_generator = await gpt4.prompt(socket_id, input["msg"])
        assistant_msg = ""
        try:
            async for response_chunk in response_generator:
                delta = response_chunk["choices"][0]["delta"]
                if "content" in delta:
                    await ws.send(delta["content"])
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
        finally:
            await ws.send("END")
