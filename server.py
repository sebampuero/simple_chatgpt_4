from logging.handlers import RotatingFileHandler
from application.server.routes import *
from sanic import Sanic
import logging, os

ENV = os.getenv("ENV")
SUB_DIRECTORY = os.getenv("SUBDIRECTORY")
DOMAIN = os.getenv("DOMAIN")
PORT = 9191 if ENV == "PROD" else 9292

log_file = 'log.log' if ENV == "PROD" else "test.log"
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler = RotatingFileHandler(os.path.abspath(os.path.join(os.path.dirname(__file__), log_file)))
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG) if os.getenv("ENV") == "DEV" else logger.setLevel(logging.INFO)

app = Sanic("chatgpt4")
app.add_route(login_code, f"{SUB_DIRECTORY}/login-code", methods=["POST"])
app.add_route(serve_index, f"{SUB_DIRECTORY}/", methods=["GET"])
app.add_route(serve_static, f"{SUB_DIRECTORY}/<filename:path>", methods=["GET"])
app.add_route(load_new_chat, f"{SUB_DIRECTORY}/chat/<id>/<timestamp>/<new_socket_id>/<old_socket_id>", methods=["GET"])
app.add_route(delete_chat, f"{SUB_DIRECTORY}/chat/<id>/<timestamp>", methods=["DELETE"])
app.add_route(get_chats_for_user, f"{SUB_DIRECTORY}/user", methods=["GET"])
app.add_route(set_model, f"{SUB_DIRECTORY}/model/<socket_id>", methods=["POST"])
app.add_route(search_for_chat, f"{SUB_DIRECTORY}/search_for_chat", methods=["POST"])
app.add_websocket_route(chat, f"{SUB_DIRECTORY}/ws")

app.ctx.sub_directory = SUB_DIRECTORY
app.ctx.domain = DOMAIN
app.ctx.ws_connection = f"wss://{DOMAIN}/{SUB_DIRECTORY}/ws" if ENV == "PROD" \
    else f"ws://192.168.0.14:{PORT}/ws"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)