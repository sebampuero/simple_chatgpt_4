import json
import logging

logger = logging.getLogger(__name__)

class ChatState:
    __instance = None

    def __init__(self):
        if ChatState.__instance is not None:
            raise Exception("Singleton.")
        else:
            ChatState.__instance = self
            self.map_ws_to_messages = {}
            self.map_ws_to_timestamp = {} # ws id is mapped to a timestamp because that is used as sort key in dynamodb. Very tight coupled to the source, yes
            self.map_ws_to_model = {}

    @staticmethod
    def get_instance():
        if ChatState.__instance is None:
            ChatState()
        return ChatState.__instance

    def set_language_model(self, model: str, ws_id: str):
        logger.debug(f"Set model {model} for ws id: {ws_id}")
        self.map_ws_to_model[ws_id] = model

    def get_language_model(self, ws_id: str) -> str:
        if ws_id in self.map_ws_to_model:
            return self.map_ws_to_model[ws_id]
        return ""

    def append_message(self, item: dict, ws_id: str):
        self.map_ws_to_messages[ws_id].append(item)
    
    def set_messages_with_ts(self, messages: list, ws_id: str, timestamp: int):
        self.map_ws_to_messages[ws_id] = messages
        self.map_ws_to_timestamp[ws_id] = timestamp
        logger.debug("Set new messages" + json.dumps(self.map_ws_to_messages[ws_id], indent=4))
        logger.debug("Set new ws_id to timestamp " + json.dumps(self.map_ws_to_timestamp[ws_id], indent=4))

    def get_messages_with_ts(self, ws_id: str) -> list:
        if ws_id in self.map_ws_to_messages and ws_id in self.map_ws_to_timestamp:
            logger.debug("Retrieved message" + json.dumps(self.map_ws_to_messages[ws_id], indent=4))
            logger.debug("Retrieved ws_id to timestamp" + json.dumps(self.map_ws_to_timestamp[ws_id], indent=4))
            return {
                "messages": self.map_ws_to_messages[ws_id],
                "timestamp": self.map_ws_to_timestamp[ws_id]
            }
        return {}

    def remove_ws(self, ws_id: str):
        messages = self.map_ws_to_messages.pop(ws_id, None)
        ts = self.map_ws_to_timestamp.pop(ws_id, None)
        self.map_ws_to_model.pop(ws_id, None)
        logger.debug(f"Removed info to socket id {ws_id}")
        logger.debug("Removed messages:" + str(messages))
