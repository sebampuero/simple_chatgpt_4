from sanic import Blueprint
from server.handlers.login import login_code, refresh_token
from server.handlers.chat import load_new_chat, delete_chat, get_chats_for_user, set_model, search_for_chat
from server.handlers.models import get_available_models

bp = Blueprint('routes')

bp.add_route(login_code, '/login-code', methods=["POST"])
bp.add_route(load_new_chat, '/chat/<id>/<timestamp>/<new_socket_id>/<old_socket_id>', methods=["GET"])
bp.add_route(delete_chat, '/chat/<id>/<timestamp>', methods=["DELETE"])
bp.add_route(get_chats_for_user, '/user', methods=["GET"])
bp.add_route(set_model, '/model/<socket_id>', methods=["POST"])
bp.add_route(search_for_chat, '/search_for_chat', methods=["POST"])
bp.add_route(get_available_models, '/models', methods=["GET"])
bp.add_route(refresh_token, '/refresh', methods=["POST"])