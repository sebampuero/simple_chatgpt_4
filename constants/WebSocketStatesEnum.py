from enum import Enum


class WebsocketConstants(Enum, str):
    INIT = "INIT"
    CONTENT = "CONTENT"
    ERROR = "ERROR"
    END = "END"
