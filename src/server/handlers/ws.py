from sanic import Websocket, Request
import logging
import json
from datetime import datetime

import websockets
from components.llm.DeepSeek import DeepSeek
from components.llm.GPT4 import GPT4
from components.llm.Mistral import Mistral
from components.llm.Claude import Claude
from components.repository.DDBRepository import DDBRepository
from components.chat.ChatState import ChatState
from constants.WebSocketStatesEnum import WebsocketConstants
from models.WebSocketMessageModel import WebSocketMessageModel
from exceptions.Exceptions import UnsupportedDataTypeException

logger = logging.getLogger("ChatGPT")

language_categories = {
    "GPT4": GPT4(),
    "Mistral": Mistral(),
    "Claude": Claude(),
    "DeepSeek": DeepSeek()
}


async def chat(request: Request, ws: Websocket):
    client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    logger.info(f"Client connected via WS: {client_ip}")
    chat_state = ChatState.get_instance()
    async def close_connection(session_id : str):
        await chat_state.remove_ws(session_id)
        await ws.close()

    async def handle_general_error(session_id: str):
        await ws.send(json.dumps({"type": WebsocketConstants.ERROR}))
        await close_connection(session_id)
        await DDBRepository().store_chat(await chat_state.get_chat_state(session_id))
    
    while True:
        # this "unique" value is used to track message in frontend, so that frontend can append
        # incoming messages to the same div bubble
        assistant_message_unique_id = datetime.timestamp(datetime.now())
        try:
            input_raw = await ws.recv()
            if type(input_raw) != str:
                raise UnsupportedDataTypeException("Unsupported data type, string was expected")
            input_json = json.loads(input_raw)
            session_id = input_json["session_id"]
            await chat_state.append_message(
                {
                    "role": "user",
                    "image": input_json["image"],
                    "content": input_json["msg"],
                },
                session_id
            )
            category = await chat_state.get_language_category(session_id)
            llm = await chat_state.get_language_model(session_id)
            category_instance = language_categories[category]
            category_instance.set_model(llm)
            logger.debug(f"Using model: {llm} and category {category}")
            chat_state_obj = await chat_state.get_chat_state(session_id)
            response_generator = await category_instance.prompt(
                chat_state_obj.messages
            )
            assistant_msg = ""
            async for response_content in category_instance.retrieve_response(
                    response_generator
                ):
                await ws.send(
                    WebSocketMessageModel(
                        content=response_content,
                        timestamp=assistant_message_unique_id,
                        type=WebsocketConstants.CONTENT,
                    ).model_dump_json(by_alias=True)
                )
                assistant_msg += response_content
            await ws.send(
                WebSocketMessageModel(
                    content=WebsocketConstants.END,
                    timestamp=assistant_message_unique_id,
                    type=WebsocketConstants.CONTENT,
                ).model_dump_json(by_alias=True)
            )
            await chat_state.append_message(
                {
                    "role": "assistant",
                    "content": assistant_msg,
                    "language_model": await chat_state.get_language_model(session_id),
                },
                session_id,
            )
            await DDBRepository().store_chat(await chat_state.get_chat_state(session_id))
        except UnsupportedDataTypeException:
            logger.error(f"Client IP {client_ip} sent unsupported data type")
            await ws.send(json.dumps({"type": WebsocketConstants.ERROR}))
            continue
        except json.JSONDecodeError:
            logger.debug(f"Client IP {client_ip} sent unsupported command")
            continue
        except websockets.exceptions.ConnectionClosedError as e:
            logger.error(str(e), exc_info=True)
            await handle_general_error(session_id)
        except websockets.exceptions.ConnectionClosedOK as e:
            logger.info(f"Connection was closed by the client: {str(e)}. Trying to dump chat state to db")
            await DDBRepository().store_chat(await chat_state.get_chat_state(session_id))
        except websockets.exceptions.ConnectionClosed as e:
            logger.info(f"Connection was closed by the client: {str(e)}. Trying to dump chat state to db")
            await DDBRepository().store_chat(await chat_state.get_chat_state(session_id))
        except Exception as e:
            logger.error(str(e), exc_info=True)
            await handle_general_error(session_id)
