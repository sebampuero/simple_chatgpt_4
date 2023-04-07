from components.chat_code_repository.ChatCode import ChatCode
from components.database.Database import Database

class CodeRepository:
    def __init__(self, database: Database):
        self.db = database

    def get_code(self, code: str) -> ChatCode:
        sql = "SELECT * FROM chat_codes WHERE code = %s"
        result = self.db.fetch_one(sql, code)
        if result:
            id, code, date_obj, count, max_uses = result
            date_str = date_obj.isoformat()
            return ChatCode(id, code, date_str, count, max_uses)
        else:
            return None
    
    def incr_code_uses(self, code: ChatCode):
        sql = "UPDATE chat_codes SET count = %s WHERE code = %s"
        res = self.db.execute(sql, code.count + 1, code.code)
        return res

    def update_code(self, code: ChatCode):
        sql = "UPDATE chat_codes SET date = %s, count = %s WHERE code = %s"
        res = self.db.execute(sql, code.date, code.count, code.code)
        return res
