import os
import logging
import json
from datetime import datetime
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Content, Part
from sanic import Websocket
from .BaseModel import BaseModel
from typing import List, Any, Generator

vertexai.init(project=os.getenv("PROJECT_ID"), location="us-central1")

logger = logging.getLogger("ChatGPT")


class Gemini(BaseModel):
    def _from_own_format_to_model_format(self, chats: list) -> list:
        output = []
        for item in chats:
            if item["role"] == "assistant":
                output.append(
                    Content(role="model", parts=[Part.from_text(item["content"])])
                )
            else:
                output.append(
                    Content(role="user", parts=[Part.from_text(item["content"])])
                )
        return output

    async def prompt(self, messages: list) -> Generator[Any, Any, None]:
        try:
            prompt = self._from_own_format_to_model_format(messages)
            model = GenerativeModel(self.model)
            response = await model.generate_content_async(prompt, stream=True)
            return response
        except Exception as e:
            logger.error(f"There was an error {str(e)}", exc_info=True)
            raise Exception(str(e))

    def _extract_content(self, response_chunk: Any) -> str:
        return response_chunk.text
