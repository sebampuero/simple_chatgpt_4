from sanic import Sanic
from server.routes import bp
from server.logging import setup_logging
from constants.AppConstants import AppConstants
from middleware.authentication import authenticate_requests

from server.handlers.ws import chat

app = Sanic(AppConstants.APP_NAME)
setup_logging(app.config.ROOT_LOG_LEVEL, app.config.APP_LOG_LEVEL)
app.blueprint(bp, url_prefix=app.config.SUB_DIRECTORY + "/api")
app.add_websocket_route(chat, f"{app.config.SUB_DIRECTORY}/ws")
app.register_middleware(authenticate_requests, "request")

app.ctx.sub_directory = app.config.SUB_DIRECTORY
app.ctx.domain = app.config.DOMAIN
app.ctx.ws_connection = (
    f"wss://{app.config.DOMAIN}/{app.config.SUB_DIRECTORY}/ws"
    if app.config.ENV == "PROD"
    else f"ws://192.168.0.14:{app.config.PORT}/ws"
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=app.config.PORT)
