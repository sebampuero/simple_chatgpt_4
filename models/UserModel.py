from pydantic import BaseModel

class UserModel(BaseModel):
    email: str