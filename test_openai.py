"""
Script de prueba para verificar la conexión con OpenAI/OpenRouter
"""
import asyncio
import logging
from App.Utils.open_ai import OpenAIClient
from App.Core.logging import setup_logging

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)

async def test_openai():
    try:
        logger.info("=" * 50)
        logger.info("🧪 INICIANDO PRUEBA DE OPENAI/OPENROUTER")
        logger.info("=" * 50)
        
        # Inicializar cliente
        client = OpenAIClient()
        
        # Texto de prueba
        test_text = """
        La inteligencia artificial (IA) es una rama de la informática que busca 
        crear sistemas capaces de realizar tareas que normalmente requieren 
        inteligencia humana. Incluye áreas como el aprendizaje automático, 
        procesamiento del lenguaje natural y visión por computadora.
        """
        
        logger.info("\n📝 Texto de prueba:")
        logger.info(test_text.strip())
        logger.info("\n🤖 Generando resumen...")
        
        # Generar resumen
        result = await client.generate_summary(test_text)
        
        logger.info("\n" + "=" * 50)
        logger.info("✅ RESULTADO EXITOSO")
        logger.info("=" * 50)
        logger.info(f"\n📄 Resumen generado:")
        logger.info(result["data"]["summary"])
        logger.info(f"\n📊 Metadatos:")
        logger.info(f"   - Modelo: {result['model']}")
        logger.info(f"   - Tiempo: {result['response_time']:.2f}s")
        logger.info(f"   - Tokens: {result['usage']['total_tokens']}")
        logger.info(f"      - Prompt: {result['usage']['prompt_tokens']}")
        logger.info(f"      - Completion: {result['usage']['completion_tokens']}")
        
        return True
        
    except Exception as e:
        logger.error("\n" + "=" * 50)
        logger.error("❌ ERROR EN LA PRUEBA")
        logger.error("=" * 50)
        logger.error(f"Tipo de error: {type(e).__name__}")
        logger.error(f"Mensaje: {e}")
        logger.exception("Traceback completo:")
        return False

if __name__ == "__main__":
    print("\n🚀 Ejecutando prueba de OpenAI/OpenRouter...\n")
    success = asyncio.run(test_openai())
    
    if success:
        print("\n✅ Prueba completada exitosamente!")
    else:
        print("\n❌ La prueba falló. Revisa los logs arriba.")
