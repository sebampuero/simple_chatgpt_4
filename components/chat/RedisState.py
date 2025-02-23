import redis
import logging
import json

from config import config as appconfig

logger = logging.getLogger("ChatGPT")


class RedisState():

    def __init__(self):
        self.r = redis.Redis(
            host=appconfig.REDIS_HOST, 
            port=int(appconfig.REDIS_PORT), 
            db=0, 
            charset="utf-8", 
            decode_responses=True)

    def set_language_model_category(self, model: str, category: str, ws_id: str):
        try:
            self.r.hset(f"ws:{ws_id}", mapping={
                "model": model,
                "category": category
            })
        except redis.exceptions.RedisError as e:
            logger.error(f"Error setting language model: {e}")

    def get_language_category(self, ws_id: str) -> str:
        try:
            return self.r.hget(f"ws:{ws_id}", "category")
        except redis.exceptions.RedisError as e:
            logger.error(f"Error getting language category: {e}")
            return ""

    def get_language_model(self, ws_id: str) -> str:
        try:
            return self.r.hget(f"ws:{ws_id}", "model")
        except redis.exceptions.RedisError as e:
            logger.error(f"Error getting language model: {e}")
            return ""

    def append_message(self, item: dict, ws_id: str):
        try:
            msg_list = json.loads(self.r.hget(f"ws:{ws_id}", "messages"))
            msg_list.append(item)
            self.r.hset(f"ws:{ws_id}", mapping={
                "messages": json.dumps(msg_list)
            })
        except redis.exceptions.RedisError as e:
            logger.error(f"Error appending message: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")

    def set_messages_with_ts(self, messages: list, ws_id: str, timestamp: int):
        try:
            messages = json.dumps(messages)
            self.r.hset(f"ws:{ws_id}", mapping={
                "messages": messages,
                "timestamp": str(timestamp)
            })
        except redis.exceptions.RedisError as e:
            logger.error(f"Error setting messages with timestamp: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Error encoding JSON: {e}")

    def get_messages_with_ts(self, ws_id: str) -> dict:
        try:
            messages = json.loads(self.r.hget(f"ws:{ws_id}", "messages"))
            timestamp = int(self.r.hget(f"ws:{ws_id}", "timestamp"))
            return {
                "messages": messages,
                "timestamp": timestamp
            }
        except redis.exceptions.RedisError as e:
            logger.error(f"Error getting messages with timestamp: {e}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
            return {}

    def remove_ws(self, ws_id: str):
        try:
            self.r.delete(f"ws:{ws_id}")
        except redis.exceptions.RedisError as e:
            logger.error(f"Error removing websocket ID {ws_id}: {e}")
