import abc
import logging
from typing import Any, AsyncGenerator, Generator
from sanic import Sanic
from constants.AppConstants import AppConstants
app = Sanic(AppConstants.APP_NAME)

logger = logging.getLogger("ChatGPT")

class BaseModel(abc.ABC):
    def set_model(self, model: str):
        logger.debug(f"Set model {model} for instance {self}")
        self.model = model
        self.max_tokens = app.config.MAX_LLM_TOKENS

    @abc.abstractmethod
    def _from_own_format_to_model_format(self, chats: list) -> list:
        pass

    @abc.abstractmethod
    async def prompt(self, messages: list) -> Generator[Any, Any, None]:
        pass

    async def retrieve_response(
        self, response_generator
    ) -> AsyncGenerator[str, None]:
        async for response_chunk in response_generator:
            content = self._extract_content(response_chunk)
            if content:
                yield content

    @abc.abstractmethod
    def _extract_content(self, response_chunk: Any) -> str:
        pass
