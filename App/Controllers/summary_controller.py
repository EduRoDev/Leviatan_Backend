from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from App.Utils.db_sessions import get_db
from App.Services.summary_services import SummaryService
from App.Services.document_services import DocumentService
from App.Utils.open_ai import OpenAIClient
from App.Utils.auth_utils import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/summary", tags=["summary"])

@router.get("/resumen/{document_id}")
def get_summary(document_id: int, db: Session = Depends(get_db),current_user: dict = Depends(get_current_user)):
    summary = SummaryService(db).get_summary_document_id(document_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary

@router.post("/create/{document_id}")
async def create_summary(document_id: int, db: Session = Depends(get_db),current_user: dict = Depends(get_current_user)):
    try:
        document_service = DocumentService(db)
        summary_service = SummaryService(db)
        openai_client = OpenAIClient()
        
        logger.info(f"📄 Creando resumen para documento {document_id}")
        
        document = document_service.get_document(document_id)
        
        if not document:
            logger.error(f"❌ Documento {document_id} no encontrado")
            raise HTTPException(status_code=404, detail="Document not found")
        
        logger.info(f"📝 Documento encontrado: {document.title} ({len(document.content)} caracteres)")
        
        # Generar resumen
        logger.info(f"🤖 Enviando contenido al modelo de IA...")
        result = await openai_client.generate_summary(document.content)
        
        if not result:
            logger.error("❌ El resultado del modelo es None")
            raise HTTPException(status_code=500, detail="El modelo no devolvió ningún resultado")
        
        if "data" not in result:
            logger.error(f"❌ Falta 'data' en resultado: {result}")
            raise HTTPException(status_code=500, detail="Formato de respuesta inválido del modelo")
        
        if "summary" not in result["data"]:
            logger.error(f"❌ Falta 'summary' en data: {result['data']}")
            raise HTTPException(status_code=500, detail="El modelo no generó un resumen")
        
        summary_content = result["data"]["summary"]
        logger.info(f"✅ Resumen generado: {len(summary_content)} caracteres")
        
        # Guardar el resumen
        logger.info(f"💾 Guardando resumen en la base de datos...")
        saved_summary = summary_service.save_summary(summary_content, document_id)
        
        if not saved_summary:
            logger.error("❌ Error al guardar el resumen en la BD")
            raise HTTPException(status_code=500, detail="Error saving summary")
        
        logger.info(f"✅ Resumen guardado exitosamente con ID {saved_summary.id}")
        
        return {
            "id": saved_summary.id,
            "content": saved_summary.content,
            "document_id": saved_summary.document_id,
            "meta": {
                "model": result.get("model"),
                "response_time": result.get("response_time"),
                "tokens_used": result.get("usage", {}).get("total_tokens", 0)
            }
        }
        
    
    except Exception as e:        
        logger.error(f"❌ Error inesperado en create_summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/test-model")
async def test_model():
    """Endpoint de prueba para verificar que el modelo responde correctamente"""
    try:
        openai_client = OpenAIClient()
        
        test_text = """
        La inteligencia artificial es una rama de la informática que se centra en 
        la creación de sistemas capaces de realizar tareas que normalmente requieren 
        inteligencia humana. Esto incluye el aprendizaje automático, el procesamiento 
        del lenguaje natural y la visión por computadora.
        """
        
        logger.info("🧪 Iniciando prueba del modelo...")
        result = await openai_client.generate_summary(test_text)
        
        return {
            "status": "success",
            "message": "El modelo respondió correctamente",
            "summary": result["data"]["summary"],
            "meta": {
                "model": result.get("model"),
                "response_time": result.get("response_time"),
                "tokens": result.get("usage", {})
            }
        }
    except Exception as e:
        logger.error(f"❌ Error en prueba: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__
        }