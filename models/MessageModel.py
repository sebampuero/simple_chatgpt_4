from pydantic import BaseModel, Field

class MessageModel(BaseModel):
    role: str
    content: str
    image: str = Field(default="")
    language_model: str = Field(default="")