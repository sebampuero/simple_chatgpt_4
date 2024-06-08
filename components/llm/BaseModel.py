import abc
import json
from sanic import Websocket
from typing import List, Any, Dict, Awaitable, Generator

class BaseModel(abc.ABC):
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
                await ws.send(json.dumps({"content": content, "timestamp": message_timestamp, "type": "CONTENT"}))
                assistant_msg += content
        return assistant_msg

    @abc.abstractmethod
    def _extract_content(self, response_chunk: Any) -> str:
        pass
