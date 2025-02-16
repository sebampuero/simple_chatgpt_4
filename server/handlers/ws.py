from sanic import Websocket, Request
import logging
import json
from datetime import datetime
from components.llm.GPT4 import GPT4
from components.llm.Mistral import Mistral
from components.llm.Claude import Claude
from components.repository.DDBRepository import DDBRepository
from components.chat.ChatState import ChatState
from constants.WebsocketConstants import WebsocketConstants

logger = logging.getLogger("ChatGPT")

language_categories = {
    "GPT4": GPT4(),
    "Mistral": Mistral(),
    "Claude": Claude()
}

async def chat(request: Request, ws: Websocket):
    client_ip = request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
    socket_id = str(id(ws))
    user_email = ""
    chat_id = ""
    logger.info(f"Client connected via WS: {client_ip} and socket_id {socket_id}")
    await ws.send(json.dumps({"socket_id": socket_id, "type": WebsocketConstants.INIT}))
    chat_state = ChatState.get_instance()
    chat_state.set_messages_with_ts([], socket_id, int(datetime.now().timestamp()))

    async def close_connection():
        chat_state.remove_ws(socket_id)
        await ws.close()

    async def store_chat():
        await DDBRepository().store_chat(chat_state.get_messages_with_ts(socket_id), user_email, chat_id)

    while True:
        message_timestamp = datetime.timestamp(datetime.now())
        try:
            input_raw = await ws.recv()
        except:
            logger.error(f"Unexpected exception, most probably {client_ip} closed the websocket connection", exc_info=True)
            await store_chat()
            await close_connection()
            break
        if not input_raw or "email" not in input_raw:
            await close_connection()
            break
        try:
            input_json = json.loads(input_raw)
        except json.JSONDecodeError:
            logger.debug(f"Client IP {client_ip} sent unsupported command")
            await ws.close()
            break
        user_email = input_json['email']
        chat_id = input_json['chat_id']
        chat_state.append_message({
            "role": "user",
            "image": input_json['image'],
            "content": input_json['msg']
        }, socket_id)
        try:
            category = chat_state.get_language_category(socket_id)
            llm = chat_state.get_language_model(socket_id)
            category_instance = language_categories[category]
            category_instance.set_model(llm)
            logger.debug(f"Using model: {llm} and category {category}")
            response_generator = await category_instance.prompt(chat_state.get_messages_with_ts(socket_id)['messages'])
            assistant_msg = await category_instance.process_response(response_generator, ws, int(message_timestamp))
            await ws.send(json.dumps({"content": WebsocketConstants.END, "timestamp": int(message_timestamp), "type": WebsocketConstants.CONTENT}))
            chat_state.append_message({
                "role": "assistant",
                "content": assistant_msg,
                "language_model": chat_state.get_language_model(socket_id)
            }, socket_id)
        except Exception as e:
            logger.error(str(e), exc_info=True)
            await store_chat()
            await ws.send(json.dumps({"type": WebsocketConstants.ERROR}))
