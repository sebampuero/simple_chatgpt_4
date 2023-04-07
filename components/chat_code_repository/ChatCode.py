from dataclasses import dataclass

@dataclass
class ChatCode:
    id: int
    code: str
    date: str
    count: int
    max_uses: int