import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        # Reading .env file
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
        self.TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")


config = Config()
