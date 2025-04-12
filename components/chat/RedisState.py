from typing import Any, Dict
import redis
import logging
import json

from config import config as appconfig
from models.ChatModel import ChatModel

logger = logging.getLogger("ChatGPT")


class RedisState: # TODO: use async!!
    def __init__(self):
        self.r = redis.Redis(
            host=appconfig.REDIS_HOST,
            port=int(appconfig.REDIS_PORT),
            db=0,
            charset="utf-8",
            decode_responses=True,
        )

    def set_language_model_category(self, model: str, category: str, ws_id: str):
        try:
            logger.debug(f"Setting language model {model} and category {category} for websocket ID {ws_id}")
            self.r.hset(f"ws:{ws_id}", mapping={"model": model, "category": category})
        except redis.exceptions.RedisError as e:
            logger.error(f"Error setting language model: {e}")

    def get_language_category(self, ws_id: str) -> str:
        try:
            logger.debug(f"Getting language category for websocket ID {ws_id}")
            return self.r.hget(f"ws:{ws_id}", "category")
        except redis.exceptions.RedisError as e:
            logger.error(f"Error getting language category: {e}")
            return ""

    def get_language_model(self, ws_id: str) -> str:
        try:
            logger.debug(f"Getting language model for websocket ID {ws_id}")
            return self.r.hget(f"ws:{ws_id}", "model")
        except redis.exceptions.RedisError as e:
            logger.error(f"Error getting language model: {e}")
            return ""

    def append_message(self, item: Dict[str, Any], ws_id: str):
        try:
            logger.debug(f"Appending message {item} to websocket ID {ws_id}")
            chat_state_dict = json.loads(self.r.hget(f"ws:{ws_id}", "chat_state"))
            chat_state_dict["messages"].append(item)
            self.r.hset(f"ws:{ws_id}", mapping={"chat_state": json.dumps(chat_state_dict)})
        except redis.exceptions.RedisError as e:
            logger.error(f"Error appending message: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")

    def set_chat_state(self, chat_state: ChatModel, ws_id: str):
        try:
            logger.debug(f"Setting messages for websocket ID {ws_id}: {chat_state}")
            self.r.hset(
                f"ws:{ws_id}",
                mapping={"chat_state": chat_state.model_dump_json()},
            )
        except redis.exceptions.RedisError as e:
            logger.error(f"Error setting messages with timestamp: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Error encoding JSON: {e}")

    def get_chat_state(self, ws_id: str) -> ChatModel:
        try:
            logger.debug(f"Getting chat for websocket ID {ws_id}")
            chat_state = json.loads(self.r.hget(f"ws:{ws_id}", "chat_state"))
            return ChatModel.model_validate(chat_state)
        except redis.exceptions.RedisError as e:
            logger.error(f"Error getting messages with timestamp: {e}")
            return ChatModel()
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
            return ChatModel()

    def remove_ws(self, ws_id: str):
        try:
            logger.debug(f"Removing websocket ID {ws_id}")
            self.r.delete(f"ws:{ws_id}")
        except redis.exceptions.RedisError as e:
            logger.error(f"Error removing websocket ID {ws_id}: {e}")

    def load_new_chat_state(self, new_chat_state: ChatModel, ws_id: str):
        try:
            logger.debug(f"Loading new state for websocket ID {ws_id}: {new_chat_state}")
            self.r.hset(f"ws:{ws_id}", mapping={"chat_state": new_chat_state.model_dump_json()})
        except redis.exceptions.RedisError as e:
            logger.error(f"Error clearing state for websocket ID {ws_id}: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
        except Exception as e:
            logger.error(f"Unexpected error clearing state for websocket ID {ws_id}: {e}")
