import json
import logging
from .RedisState import RedisState

logger = logging.getLogger("ChatGPT")

class ChatState:
    __instance = None

    def __init__(self):
        if ChatState.__instance is not None:
            raise Exception("Singleton.")
        else:
            ChatState.__instance = self
            self.redis = RedisState()

    @staticmethod
    def get_instance():
        if ChatState.__instance is None:
            ChatState()
        return ChatState.__instance

    def set_language_model_category(self, model: str, category: str, ws_id: str):
        self.redis.set_language_model_category(model, category, ws_id)

    def get_language_category(self, ws_id: str) -> str:
        return self.redis.get_language_category(ws_id)
    
    def get_language_model(self, ws_id: str) -> str:
        return self.redis.get_language_model(ws_id)

    def append_message(self, item: dict, ws_id: str):
        self.redis.append_message(item, ws_id)
    
    def set_messages_with_ts(self, messages: list, ws_id: str, timestamp: int):
        self.redis.set_messages_with_ts(messages, ws_id, timestamp)

    def get_messages_with_ts(self, ws_id: str) -> dict:
        return self.redis.get_messages_with_ts(ws_id)

    def remove_ws(self, ws_id: str):
        self.redis.remove_ws(ws_id)
