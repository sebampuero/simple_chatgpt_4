from pydantic import BaseModel

from constants.WebSocketStatesEnum import WebsocketConstants

class WebSocketMessageModel(BaseModel):
    content: str
    type: WebsocketConstants