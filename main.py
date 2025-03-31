from sanic import Sanic
from server.routes import bp
from config import config
from server.logging import setup_logging
from config import config as appconfig
from constants.AppConstants import AppConstants
from middleware.authentication import authenticate_requests

from server.handlers.ws import chat

setup_logging(appconfig.ROOT_LOG_LEVEL, config.APP_LOG_LEVEL)
app = Sanic(AppConstants.APP_NAME)
app.blueprint(bp, url_prefix=appconfig.SUB_DIRECTORY + "/api")
app.add_websocket_route(chat, f"{appconfig.SUB_DIRECTORY}/ws")
app.register_middleware(authenticate_requests, "request")

app.ctx.sub_directory = appconfig.SUB_DIRECTORY
app.ctx.domain = appconfig.DOMAIN
app.ctx.ws_connection = (
    f"wss://{appconfig.DOMAIN}/{appconfig.SUB_DIRECTORY}/ws"
    if appconfig.ENV == "PROD"
    else f"ws://192.168.0.14:{appconfig.PORT}/ws"
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=appconfig.PORT)
