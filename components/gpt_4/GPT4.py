import openai
import os
import logging

logger = logging.getLogger(__name__)

openai.api_key = os.getenv("OPENAI_KEY")

class GPT4: #TODO: unit test, somehow
    __instance = None

    def __init__(self):
        if GPT4.__instance is not None:
            raise Exception("Singleton class. Use getInstance() method to get an instance.")
        else:
            self.map_messages = {}
            GPT4.__instance = self

    @staticmethod
    def getInstance():
        if GPT4.__instance is None:
            GPT4()
        return GPT4.__instance

    def reset_history(self, websocket_id: str) -> None:
        if websocket_id not in self.map_messages:
            return
        self.map_messages[websocket_id].clear()

    def remove_socket_id(self, websocket_id: str) -> None:
        self.map_messages.pop(websocket_id, None)

    def append_to_msg_history_as_assistant(self, websocket_id: str, message: str):
        self.map_messages[websocket_id].append({"role": "assistant", "content": message})

    async def prompt(self, websocket_id: str, input: str):
        if websocket_id not in self.map_messages:
            self.map_messages[websocket_id] = []
        self.map_messages[websocket_id].append({"role": "user", "content": input})
        response = await openai.ChatCompletion.acreate(
                model="gpt-4-0613",
                messages=self.map_messages[websocket_id],
                max_tokens=850,
                temperature=0.5,
                top_p=0,
                frequency_penalty=0,
                presence_penalty=1,
                stream=True
            )  
        return response
