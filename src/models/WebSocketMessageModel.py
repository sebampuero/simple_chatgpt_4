from pydantic import BaseModel, Field

from constants.WebSocketStatesEnum import WebsocketConstants

class WebSocketMessageModel(BaseModel):
    content: str
    unique_message_identifier: float = Field(alias="timestamp")
    type: WebsocketConstants