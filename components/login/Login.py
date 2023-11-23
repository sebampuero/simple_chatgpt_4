from components.repository.Repository import Repository
from sanic import Sanic

class Login:

    def __init__(self) -> None:
        self.app =  Sanic.get_app("chatgpt4")
        self.repo =  Repository()

    def check_user_is_authorized(self,email: str) -> bool:
        return not self.repo.get_user_by_email(email) == None