from sanic import Request
from sanic.response import HTTPResponse, json as sanicjson
from components.repository.DDBRepository import DDBRepository
from components.elasticsearch.ElasticClient import ElasticClient
from components.chat.ChatState import ChatState
from models.ChatModel import ChatModel
import json

async def load_new_chat_state(request: Request, session_id: str):
    if not session_id:
        return HTTPResponse(status=400)
    body = request.json
    email = body.get("email")
    if email is None or email.strip() == "":
        return HTTPResponse(status=400)
    chat_state = ChatState.get_instance()
    await chat_state.load_new_chat_state(
        ChatModel(
            user_email=email, 
            messages=[]), 
        session_id
    )
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
    es = await ElasticClient.get_instance()
    chats = await es.search_chats_by_keyword(
        keyword=keywords, email_address=email_address
    )
    return sanicjson({"chats": chats})


async def load_new_chat(
    request: Request, id: str, session_id: str
):
    if id is None or id.strip() == "":
        return HTTPResponse(status=400)
    chat_data = await DDBRepository().get_chat_by_id(id)
    if chat_data is None:
        return HTTPResponse(status=404)
    if session_id:
        chat_state = ChatState.get_instance()
        await chat_state.set_chat_state(
            ChatModel(
                user_email=chat_data["user_email"], 
                messages=chat_data["messages"], 
                timestamp=chat_data["timestamp"], 
                chat_id=id), 
            session_id
        )
        return sanicjson({"body": chat_data}, status=200)
    return sanicjson({"body": chat_data}, status=206)


async def set_model(request: Request, session_id: str):
    body = request.json
    model = body.get("model")
    category = body.get("category")
    chat_state = ChatState.get_instance()
    if chat_state:
        await chat_state.set_language_model_category(model, category, session_id)
        return HTTPResponse(status=200)
    return HTTPResponse(status=500)


async def delete_chat(request: Request, id: str, timestamp: str):
    if id.strip() == "":
        return HTTPResponse(status=400)
    await DDBRepository().delete_chat_by_id(id, int(timestamp))
    return HTTPResponse(status=204)
