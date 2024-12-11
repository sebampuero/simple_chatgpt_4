import os


class Config:
    def __init__(self):
        self.ENV = os.getenv("ENV")
        self.SUB_DIRECTORY = os.getenv("SUBDIRECTORY")
        self.DOMAIN = os.getenv("DOMAIN")
        self.PORT = 9191 if self.ENV == "PROD" else 9292
        self.ROOT_LOG_LEVEL = os.getenv("ROOT_LOG_LEVEL", "INFO").upper()
        self.APP_LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "INFO").upper()


config = Config()
