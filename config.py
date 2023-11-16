import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        # Reading .env file
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)

        self.TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

        self.TELEGRAM_ALLOWED_USERS = os.environ.get("TELEGRAM_ALLOWED_USERS").split(";") if os.environ.get("TELEGRAM_ALLOWED_USERS") else []
        if isinstance(self.TELEGRAM_ALLOWED_USERS, str):
            self.TELEGRAM_ALLOWED_USERS = [self.TELEGRAM_ALLOWED_USERS]

        self.CONFIRMATION_CODE = os.environ.get("CONFIRMATION_CODE")

        self.MT_IP_ADDRESS = os.environ.get("MT_IP_ADDRESS")
        self.MT_USER = os.environ.get("MT_USER")
        self.MT_PASSWORD = os.environ.get("MT_PASSWORD")
        self.COMMAND = os.environ.get("COMMAND")
        self.RESTRICT_ADDRESSES = os.environ.get("RESTRICT_ADDRESSES").split(";") if os.environ.get("RESTRICT_ADDRESSES") else []
        self.SCRIPT = os.environ.get("SCRIPT")


config = Config()
