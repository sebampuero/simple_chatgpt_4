import logging
from .BaseModel import BaseModel
from mistralai.async_client import MistralAsyncClient # TODO: migrate https://github.com/mistralai/client-python/blob/main/MIGRATION.md
from mistralai.models.chat_completion import ChatMessage
from typing import Any, Generator
from config import config as appconfig

API_KEY = appconfig.MISTRAL_API_KEY

logger = logging.getLogger("ChatGPT")


class Mistral(BaseModel):
    def _from_own_format_to_model_format(self, chats: list) -> list:
        output = []
        for item in chats:
            if item["role"] == "assistant":
                output.append(ChatMessage(role="assistant", content=item["content"]))
                continue
            if item["image"] == "":
                output.append(ChatMessage(role="user", content=item["content"]))
            else:
                message = {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": item["content"]
                        },
                        {
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{item['image']}"
                        }
                    ]
                }
                output.append(message)
        return output

    async def prompt(self, messages: list) -> Generator[Any, Any, None]:
        try:
            prompt = self._from_own_format_to_model_format(messages)
            client = MistralAsyncClient(api_key=API_KEY)
            response = client.chat_stream(model=self.model, messages=prompt)
            return response
        except Exception as e:
            logger.error(f"There was an error {str(e)}", exc_info=True)
            raise Exception(str(e))

    def _extract_content(self, response_chunk: Any) -> dict:
        return response_chunk.choices[0].delta.content