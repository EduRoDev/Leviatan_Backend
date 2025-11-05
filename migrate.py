"""
Script para ejecutar migraciones de Alembic en producción
"""
import subprocess
import sys
import logging
from App.Core.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def run_migrations():
    """Ejecuta las migraciones de Alembic"""
    try:
        logger.info("🔄 Iniciando migraciones de base de datos...")
        
        # Ejecutar migraciones
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info("✅ Migraciones completadas exitosamente")
        logger.info(f"Output: {result.stdout}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error en migraciones: {e}")
        logger.error(f"Stderr: {e.stderr}")
        logger.error(f"Stdout: {e.stdout}")
        return False
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
