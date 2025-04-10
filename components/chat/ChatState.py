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
    def get_instance() -> "ChatState":
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

    def set_chat_state(self, chat_state: dict, ws_id: str):
        self.redis.set_chat_state(chat_state, ws_id)

    def get_chat_state(self, ws_id: str) -> dict:
        return self.redis.get_chat_state(ws_id)

    def remove_ws(self, ws_id: str):
        self.redis.remove_ws(ws_id)

    def load_new_chat_state(self, new_chat_state: dict, ws_id: str):
        self.redis.load_new_chat_state(new_chat_state, ws_id)
