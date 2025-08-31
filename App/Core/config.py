import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "deepseek/deepseek-chat-v3.1:free")

    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "uploads")
    OUTPUT_FOLDER: str = os.getenv("OUTPUT_FOLDER", "outputs")
    MIN_TEXT_QUALITY_WORDS: int = int(os.getenv("MIN_TEXT_QUALITY_WORDS", "50"))

    def __init__(self):
        logging.info(f"Configuración cargada: OPENAI_MODEL={self.OPENAI_MODEL}, UPLOAD_FOLDER={self.UPLOAD_FOLDER}, OUTPUT_FOLDER={self.OUTPUT_FOLDER}")

settings = Settings()