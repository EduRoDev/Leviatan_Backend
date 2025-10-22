import logging
import sys
from pathlib import Path

def setup_logging():
    """"Configura el logging para la aplicación."""
    
    logging.basicConfig(
        level=logging.DEBUG,  # Cambiado a DEBUG para ver más detalles
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log', encoding='utf-8')
        ]
    )

    logging.getLogger("pdfplumber").setLevel(logging.WARNING)
    logging.getLogger("PyPDF2").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)  # Silenciar logs de httpx
    logging.getLogger("httpcore").setLevel(logging.WARNING)  # Silenciar logs de httpcore