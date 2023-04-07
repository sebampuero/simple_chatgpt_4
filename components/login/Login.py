from components.chat_code_repository.CodeRepository import CodeRepository
from components.chat_code_repository.ChatCode import ChatCode
from sanic import Sanic

class Login:

    def __init__(self) -> None:
        self.app =  Sanic.get_app("chatgpt4")
        self.repo =  CodeRepository(self.app.ctx.db)

    def check_code_is_correct(self,code: str) -> bool:
        return not self.repo.get_code(code) == None