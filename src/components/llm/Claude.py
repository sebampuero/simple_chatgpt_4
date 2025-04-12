import logging
from .BaseModel import BaseModel
from typing import Any
from anthropic import AsyncAnthropic
from constants.AppConstants import AppConstants
from sanic import Sanic
logger = logging.getLogger("ChatGPT")


class Claude(BaseModel):
    def _from_own_format_to_model_format(self, chats: list) -> list:
        output = []
        for item in chats:
            if item["role"] == "assistant":
                output.append({"role": "assistant", "content": item["content"]})
            else:
                output.append({"role": "user", "content": item["content"]})
        return output

    async def prompt(self, messages: list):
        try:
            prompt = self._from_own_format_to_model_format(messages)
            model = AsyncAnthropic(api_key=self.app.config.ANTHROPIC_API_KEY)
            response = await model.messages.create(
                max_tokens=self.max_tokens,
                messages=prompt,
                model=self.model,
                stream=True,
            )
            return response
        except Exception as e:
            logger.error(f"There was an error {str(e)}", exc_info=True)
            raise Exception(str(e))

    def _extract_content(self, response_chunk: Any) -> str:
        if response_chunk.type == "content_block_delta":
            return response_chunk.delta.text
        return ""
