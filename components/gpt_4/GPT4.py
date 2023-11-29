import openai
import os
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

openai.api_key = os.getenv("OPENAI_KEY")

class GPT4: 
    __instance = None

    def __init__(self):
        if GPT4.__instance is not None:
            raise Exception("Singleton class. Use getInstance() method to get an instance.")
        else:
            self.map_messages = {}
            self.map_ws_id_to_timestamp = {}
            GPT4.__instance = self

    @staticmethod
    def getInstance():
        if GPT4.__instance is None:
            GPT4()
        return GPT4.__instance

    def remove_socket_id(self, websocket_id: str) -> None:
        self.map_messages.pop(websocket_id, None)
        self.map_ws_id_to_timestamp.pop(websocket_id, None)

    def append_to_msg_history_as_assistant(self, websocket_id: str, message: str):
        self.map_messages[websocket_id].append({"role": "assistant", "content": message})

    def get_messages_info(self, ws_id: str) -> dict:
        logger.debug("Retrieved messages. " + json.dumps(self.map_messages, indent=4))
        if ws_id in self.map_messages and ws_id in self.map_ws_id_to_timestamp:
            return {
                "messages": self._from_gpt4_format_to_own_format(self.map_messages[ws_id]),
                "timestamp": self.map_ws_id_to_timestamp[ws_id]
            }
        return {}
    
    def set_messages_info(self, ws_id: str, timestamp: int, chats: list):
        self.map_messages[ws_id] = self._from_own_format_to_gpt4_format(chats)
        self.map_ws_id_to_timestamp[ws_id] = timestamp
        logger.debug("Set messages. " + json.dumps(self.map_messages, indent=4))

    def _from_own_format_to_gpt4_format(self, chats: list) -> list:
        output_list = []
        for item in chats:
            if item["role"] == "assistant":
                output_list.append(item)
                continue
            if item["image"] == "":
                new_item = {"role": item["role"], "content": item["content"]}
            else:
                new_item = {"role": item["role"], "content": []}
                new_item["content"].append({"type": "text", "text": item["content"]})
                image_url = f"data:image/jpeg;base64,{item['image']}"
                new_item["content"].append({"type": "image_url", "image_url": {"url": image_url}})
            output_list.append(new_item)
        return output_list

    def _from_gpt4_format_to_own_format(self, chats: list) -> list:
        output_list = []
        for item in chats:
            if item["role"] == "assistant":
                output_list.append(item)
                continue
            new_item = {"role": item["role"], "content": "", "image": ""}
            if isinstance(item["content"], list):
                new_item["content"] = item["content"][0]["text"]
                data_index = item["content"][1]["image_url"]["url"].index(',') + 1
                image_data = item["content"][1]["image_url"]["url"][data_index:]
                new_item["image"] = image_data
            else:
                new_item["content"] = item["content"]
            output_list.append(new_item)
        return output_list

    async def prompt(self, websocket_id: str, input: dict):
        if websocket_id not in self.map_messages:
            self.map_messages[websocket_id] = []
        if websocket_id not in self.map_ws_id_to_timestamp:
            self.map_ws_id_to_timestamp[websocket_id] = int(datetime.now().timestamp())
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
        logger.debug(f"Sending prompt with {self.map_messages[websocket_id]}")
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
