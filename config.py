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
        assert self.GOOGLE_OAUTH_CLIENT_ID
        assert self.GOOGLE_OAUTH_CLIENT_SECRET


config = Config()
