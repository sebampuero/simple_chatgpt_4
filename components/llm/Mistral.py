import os
import logging
from sanic import Websocket
from .BaseModel import BaseModel
from mistralai.async_client  import MistralAsyncClient
from mistralai.models.chat_completion import ChatMessage
from typing import List, Any, Generator

MODEL = os.getenv("MISTRAL_MODEL")
API_KEY = os.getenv("MISTRAL_API_KEY")

logger = logging.getLogger(__name__)

class Mistral(BaseModel):
    
    def _from_own_format_to_model_format(self, chats: list) -> list:
        output = []
        for item in chats:
            if item["role"] == "assistant":
                output.append(ChatMessage(role="assistant", content=item["content"]))
            else:
                output.append(ChatMessage(role="user", content=item["content"]))
        return output

    async def prompt(self, messages: list)-> Generator[Any, Any, None]:
        try:
            prompt = self._from_own_format_to_model_format(messages)
            client = MistralAsyncClient(api_key=API_KEY)
            response = client.chat_stream(model=MODEL, messages=prompt)
            return  response
        except Exception as e:
            logger.error(f"There was an error {str(e)}", exc_info=True)
            raise Exception(str(e))

    def _extract_content(self, response_chunk: Any) -> str:
        return response_chunk.choices[0].delta.content