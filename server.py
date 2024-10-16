import logging.config
import pathlib
from application.server.routes import *
from sanic import Sanic

ENV = os.getenv("ENV")
SUB_DIRECTORY = os.getenv("SUBDIRECTORY")
DOMAIN = os.getenv("DOMAIN")
PORT = 9191 if ENV == "PROD" else 9292
ROOT_LOG_LEVEL = os.getenv("ROOT_LOG_LEVEL", "INFO").upper()
APP_LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "INFO").upper()

def setup_logging():
    config_file = pathlib.Path("log_config.json")
    with open(config_file) as f_in:
        config = json.load(f_in)
    print(f"Running APP LOG LEVEL {APP_LOG_LEVEL}")
    print(f"Running ROOT LOG LEVEL {ROOT_LOG_LEVEL}")
    config["loggers"]["root"]["level"] = ROOT_LOG_LEVEL
    config["loggers"]["ChatGPT"]["level"] = APP_LOG_LEVEL
    logging.config.dictConfig(config)

setup_logging()
app = Sanic("chatgpt4")
app.add_route(login_code, f"{SUB_DIRECTORY}/api/login-code", methods=["POST"])
app.add_route(load_new_chat, f"{SUB_DIRECTORY}/api/chat/<id>/<timestamp>/<new_socket_id>/<old_socket_id>", methods=["GET"])
app.add_route(delete_chat, f"{SUB_DIRECTORY}/api/chat/<id>/<timestamp>", methods=["DELETE"])
app.add_route(get_chats_for_user, f"{SUB_DIRECTORY}/api/user", methods=["GET"])
app.add_route(set_model, f"{SUB_DIRECTORY}/api/model/<socket_id>", methods=["POST"])
app.add_route(search_for_chat, f"{SUB_DIRECTORY}/api/search_for_chat", methods=["POST"])
app.add_websocket_route(chat, f"{SUB_DIRECTORY}/ws")

app.ctx.sub_directory = SUB_DIRECTORY
app.ctx.domain = DOMAIN
app.ctx.ws_connection = f"wss://{DOMAIN}/{SUB_DIRECTORY}/ws" if ENV == "PROD" \
    else f"ws://192.168.0.14:{PORT}/ws"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
