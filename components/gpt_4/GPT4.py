import openai
import os
import logging

logger = logging.getLogger(__name__)

openai.api_key = os.getenv("OPENAI_KEY")

class GPT4: 
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

    def remove_socket_id(self, websocket_id: str) -> None:
        self.map_messages.pop(websocket_id, None)

    def append_to_msg_history_as_assistant(self, websocket_id: str, message: str):
        self.map_messages[websocket_id].append({"role": "assistant", "content": message})

    async def prompt(self, websocket_id: str, input: dict):
        if websocket_id not in self.map_messages:
            self.map_messages[websocket_id] = []
        content = input['msg'] if input['image'] == '' \
            else [{
                "type": "text",
                "text": input['msg']
            },
            {  
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{input['image']}"
                }
            }
        ]
        self.map_messages[websocket_id].append({"role": "user", "content": content})
        response = await openai.ChatCompletion.acreate(
                model="gpt-4-vision-preview",
                messages=self.map_messages[websocket_id],
                max_tokens=2000,
                temperature=0.5,
                top_p=0,
                frequency_penalty=0,
                presence_penalty=1,
                stream=True
            )  
        return response
