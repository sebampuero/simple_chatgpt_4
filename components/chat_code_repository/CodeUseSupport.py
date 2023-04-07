from components.chat_code_repository.ChatCode import ChatCode
from components.chat_code_repository.CodeRepository import CodeRepository
from sanic import Sanic
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CodeUseSupport:

    __instance = None

    def __init__(self):
        if CodeUseSupport.__instance is not None:
            raise Exception("Singleton class. Use getInstance() method to get an instance.")
        else:
            CodeUseSupport.__instance = self
            self.app = Sanic.get_app("chatgpt4")
            self.repo = CodeRepository(self.app.ctx.db)

    @staticmethod
    def getInstance():
        if CodeUseSupport.__instance is None:
            CodeUseSupport()
        return CodeUseSupport.__instance

    def max_use_reached(self, code: str) -> bool: 
        chat_code = self.repo.get_code(code)
        if chat_code.count > chat_code.max_uses:
            logger.info(f"Max use reached for {chat_code}")
            return True
        return False
    
    def update_chat_code_date_if_needed(self, code: str) -> bool:
        chat_code = self.repo.get_code(code)
        today = datetime.today().date()
        code_last_date = datetime.strptime(chat_code.date, "%Y-%m-%d").date()
        if (today - code_last_date) >= timedelta(days=1):
            chat_code.count = 0
            chat_code.date = today
            self.repo.update_code(chat_code)
            logger.info(f"Chat code {chat_code} updated")
            return True
        return False
    
    def incr_code_use_count(self, code: str) -> None:
        chat_code = self.repo.get_code(code)
        self.repo.incr_code_uses(chat_code)