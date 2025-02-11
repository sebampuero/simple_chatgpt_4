import os


class Config:
    def __init__(self):
        self.ENV = os.getenv("ENV", "DEV")
        self.SUB_DIRECTORY = os.getenv("SUBDIRECTORY", "/")
        self.DOMAIN = os.getenv("DOMAIN", "")
        self.PORT = int(os.getenv("PORT", "9292"))
        self.ROOT_LOG_LEVEL = os.getenv("ROOT_LOG_LEVEL", "INFO").upper()
        self.APP_LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "INFO").upper()
        self.GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
        self.GOOGLE_OAUTH_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
        self.ELASTIC_SEARCH_HOST = os.getenv("ES_HOST", "192.168.0.7")
        self.ELASTIC_SEARCH_PORT = os.getenv("ES_PORT", "9200")
        self.OPENAI_KEY = os.getenv("OPENAI_KEY")
        self.MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
        self.JWT_SECRET = os.getenv("JWT_SECRET")
        self.DDB_CHATS_TABLE = os.getenv("DDB_CHATS_TABLE", "chats")
        self.DDB_USERS_TABLE = os.getenv("DDB_USERS_TABLE", "authorized_users")
        assert self.GOOGLE_OAUTH_CLIENT_ID
        assert self.GOOGLE_OAUTH_CLIENT_SECRET
        assert self.OPENAI_KEY
        assert self.MISTRAL_API_KEY
        assert self.JWT_SECRET


config = Config()
