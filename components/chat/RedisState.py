import redis
import logging
import json

from config import config as appconfig

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

    def append_message(self, item: dict, ws_id: str):
        try:
            logger.debug(f"Appending message {item} to websocket ID {ws_id}")
            msg_dict = json.loads(self.r.hget(f"ws:{ws_id}", "messages"))
            msg_dict["messages"].append(item)
            self.r.hset(f"ws:{ws_id}", mapping={"messages": json.dumps(msg_dict)})
        except redis.exceptions.RedisError as e:
            logger.error(f"Error appending message: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")

    def set_messages(self, messages: dict, ws_id: str):
        try:
            logger.debug(f"Setting messages for websocket ID {ws_id}: {messages}")
            messages = json.dumps(messages)
            self.r.hset(
                f"ws:{ws_id}",
                mapping={"messages": messages},
            )
        except redis.exceptions.RedisError as e:
            logger.error(f"Error setting messages with timestamp: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Error encoding JSON: {e}")

    def get_messages(self, ws_id: str) -> dict:
        try:
            logger.debug(f"Getting messages for websocket ID {ws_id}")
            messages = json.loads(self.r.hget(f"ws:{ws_id}", "messages"))
            return messages
        except redis.exceptions.RedisError as e:
            logger.error(f"Error getting messages with timestamp: {e}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
            return {}

    def remove_ws(self, ws_id: str):
        try:
            logger.debug(f"Removing websocket ID {ws_id}")
            self.r.delete(f"ws:{ws_id}")
        except redis.exceptions.RedisError as e:
            logger.error(f"Error removing websocket ID {ws_id}: {e}")

    def load_new_chat_state(self, new_chat_state: dict, ws_id: str):
        try:
            logger.debug(f"Loading new state for websocket ID {ws_id}: {new_chat_state}")
            self.r.hset(f"ws:{ws_id}", mapping={"messages": json.dumps(new_chat_state)})
        except redis.exceptions.RedisError as e:
            logger.error(f"Error clearing state for websocket ID {ws_id}: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
        except Exception as e:
            logger.error(f"Unexpected error clearing state for websocket ID {ws_id}: {e}")
