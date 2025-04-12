from enum import Enum


class WebsocketConstants(str, Enum):
    INIT = "INIT"
    CONTENT = "CONTENT"
    ERROR = "ERROR"
    END = "END"
