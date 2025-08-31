import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "deepseek/deepseek-chat-v3.1:free")

    def __init__(self):
        logging.info(f"Configuración cargada: OPENAI_MODEL={self.OPENAI_MODEL}, OPENAI_BASE_URL={self.OPENAI_BASE_URL}")

settings = Settings()