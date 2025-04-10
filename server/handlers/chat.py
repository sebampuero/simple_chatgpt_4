from sanic import Request
from sanic.response import HTTPResponse, json as sanicjson
from components.repository.DDBRepository import DDBRepository
from components.elasticsearch.ElasticClient import ElasticClient
from components.chat.ChatState import ChatState
import json

async def clear_chat_state_for_socket(request: Request, socket_id: str):
    chat_state = ChatState.get_instance()
    chat_state.clear_state(socket_id)
    return HTTPResponse(status=200)

async def get_chats_for_user(request: Request):
    email = request.args.get("email")
    last_eval_key = request.args.get("last_eval_key")
    try:
        limit = int(request.args.get("limit"))
    except Exception:
        return HTTPResponse(status=400)
    if last_eval_key:
        try:
            last_eval_key = json.loads(last_eval_key)
        except Exception:
            return HTTPResponse(status=400)
    if email.strip() == "":
        return HTTPResponse(status=400)
    results = await DDBRepository().get_chats_by_email_paginated(
        email, last_eval_key=last_eval_key, limit=limit
    )
    chats = results["chats"]
    last_eval_key = results["last_eval_key"]
    return sanicjson({"chats": chats, "lastEvalKey": last_eval_key})


async def search_for_chat(request: Request):
    body = request.json
    keywords = body.get("keywords")
    email_address = body.get("email_address")
    chats = ElasticClient().search_chats_by_keyword(
        keyword=keywords, email_address=email_address
    )
    return sanicjson({"chats": chats})


async def load_new_chat( # TODO: change, no need for old and new socket id
    request: Request, id: str, timestamp: str, new_socket_id: str, old_socket_id: str
):
    if id is None or id.strip() == "":
        return HTTPResponse(status=400)
    chat_data = await DDBRepository().get_chat_by_id(id, int(timestamp))
    if chat_data is None:
        return HTTPResponse(status=404)
    chat_state = ChatState.get_instance()
    chat_state.set_messages(
        chat_data["messages"], new_socket_id
    )
    chat_state.remove_ws(old_socket_id)
    return sanicjson({"body": chat_data})


async def set_model(request: Request, socket_id: str):
    body = request.json
    model = body.get("model")
    category = body.get("category")
    chat_state = ChatState.get_instance()
    if chat_state:
        chat_state.set_language_model_category(model, category, socket_id)
        return HTTPResponse(status=200)
    return HTTPResponse(status=500)


async def delete_chat(request: Request, id: str, timestamp: str):
    if id.strip() == "":
        return HTTPResponse(status=400)
    await DDBRepository().delete_chat_by_id(id, int(timestamp))
    return HTTPResponse(status=204)
