import os
from dotenv import load_dotenv
import logging
import pathlib

logger = logging.getLogger(__name__)

env_path = pathlib.Path('.env')
print(f"¿Archivo .env existe? {env_path.exists()}")
print(f"Ubicación: {env_path.absolute()}")

load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL")
    
    OPENROUTER_APP_NAME: str = os.getenv("OPENROUTER_APP_NAME", "MiApp/1.0")
    OPENROUTER_SITE_URL: str = os.getenv("OPENROUTER_SITE_URL","")
    
    CHAT_API_KEY: str = os.getenv("CHAT_API_KEY")
    CHAT_MODEL: str = os.getenv("CHAT_MODEL")
    
    # Database config
    USER_DB: str = os.getenv("USER_DB")
    USER_DB_PASSWORD: str = os.getenv("USER_DB_PASSWORD")
    DB_NAME: str = os.getenv("DB_NAME")
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    def is_openrouter(self) -> bool:
        """Detecta si estamos usando OpenRouter"""
        return "openrouter.ai" in self.OPENAI_BASE_URL.lower()
    
    def validate_openai_config(self) -> bool:
        """Valida que la configuración de OpenAI/OpenRouter sea correcta"""
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY es requerida")
        
        # Validación específica según el proveedor
        if self.is_openrouter():
            # OpenRouter puede usar varios formatos de API key
            if not (self.OPENAI_API_KEY.startswith("sk-or-") or 
                   self.OPENAI_API_KEY.startswith("sk-")):
                logger.warning("API Key de OpenRouter no tiene el formato esperado")
        else:
            # OpenAI oficial
            if not self.OPENAI_API_KEY.startswith("sk-"):
                raise ValueError("OPENAI_API_KEY debe empezar con 'sk-'")
        
        if not self.OPENAI_MODEL:
            raise ValueError("OPENAI_MODEL es requerido")
        
        # Verificar que el modelo sea válido para OpenRouter
        if self.is_openrouter():
            self._log_openrouter_model_info()
        
        return True
    
    def _log_openrouter_model_info(self):
        """Log información sobre el modelo de OpenRouter"""
        logger.info(f"Usando OpenRouter con modelo: {self.OPENAI_MODEL}")
        
        # Modelos populares de OpenRouter
        popular_models = [
            "openai/gpt-3.5-turbo",
            "openai/gpt-4",
            "openai/gpt-4-turbo",
            "anthropic/claude-3-haiku",
            "anthropic/claude-3-sonnet",
            "meta-llama/llama-3.1-8b-instruct",
            "google/gemini-pro"
        ]
        
        if self.OPENAI_MODEL in popular_models:
            logger.info(f"✅ Modelo reconocido: {self.OPENAI_MODEL}")
        else:
            logger.warning(f"⚠️  Modelo no reconocido: {self.OPENAI_MODEL}")
            logger.info("Modelos populares disponibles en OpenRouter:")
            for model in popular_models[:5]:  # Mostrar solo algunos
                logger.info(f"  - {model}")
    
    def get_client_headers(self) -> dict:
        """Retorna headers específicos para el cliente"""
        headers = {}
        
        if self.is_openrouter():
            # Headers específicos de OpenRouter
            headers["HTTP-Referer"] = self.OPENROUTER_SITE_URL
            headers["X-Title"] = self.OPENROUTER_APP_NAME
        
        return headers

    def __init__(self):
        provider = "OpenRouter" if self.is_openrouter() else "OpenAI"
        logger.info(f"Configuración cargada para {provider}:")
        logger.info(f"  - Modelo: {self.OPENAI_MODEL}")
        logger.info(f"  - Base URL: {self.OPENAI_BASE_URL}")
        logger.info(f"  - Modelo de chat: {self.CHAT_MODEL}")
        if self.is_openrouter():
            logger.info(f"  - App: {self.OPENROUTER_APP_NAME}")

settings = Settings()