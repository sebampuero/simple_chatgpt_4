import abc
import json
import logging
from sanic import Websocket
from typing import Any, Generator
from constants.WebsocketConstants import WebsocketConstants

logger = logging.getLogger("ChatGPT")


class BaseModel(abc.ABC):

    def set_model(self, model: str):
        logger.debug(f"Set model {model} for instance {self}")
        self.model = model

    @abc.abstractmethod
    def _from_own_format_to_model_format(self, chats: list) -> list:
        pass

    @abc.abstractmethod
    async def prompt(self, messages: list) -> Generator[Any, Any, None]:
        pass

    async def process_response(self, response_generator, ws: Websocket, message_timestamp: int) -> str:
        assistant_msg = ""
        async for response_chunk in response_generator:
            content = self._extract_content(response_chunk)
            if content:
                await ws.send(json.dumps({"content": content, "timestamp": message_timestamp, "type": WebsocketConstants.CONTENT}))
                assistant_msg += content
        return assistant_msg

    @abc.abstractmethod
    def _extract_content(self, response_chunk: Any) -> str:
        pass
