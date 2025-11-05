from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import traceback
from App.Utils.db_sessions import get_db
from App.Utils.auth_utils import get_current_user
from App.Services.study_plan_services import StudyPlanService
from App.Services.document_services import DocumentService
from App.Utils.open_ai import OpenAIClient

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/study-plans",
    tags=["Study Plans"],
    responses={404: {"description": "Not found"}},
)


@router.post("/create/{document_id}/{level}", status_code=status.HTTP_201_CREATED)
async def create_study_plan(
    document_id: int,
    level: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    
    plan_services = StudyPlanService(db)
    document_service = DocumentService(db)
    open_ai_service = OpenAIClient()
    
    valid_levels = ["basico", "intermedio", "avanzado"]
    if level.lower() not in valid_levels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Nivel inválido. Debe ser uno de: {', '.join(valid_levels)}"
        )
    try:
        user_id = current_user["id"]
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no autenticado"
            )
        
        logger.info(f"Usuario {user_id} creando plan de estudio nivel {level} para documento {document_id}")
        
        document = document_service.get_document(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        logger.info(f"Documento {document_id} encontrado, generando plan...")
        
        ai_response = await open_ai_service.study_plan_personalized(
            document_content=document.content,
            level_plan=level
        )
        
        logger.info(f"Respuesta de IA recibida: {ai_response.keys()}")
        
        # Verificar estructura de respuesta
        if not ai_response or "data" not in ai_response:
            logger.error(f"Respuesta inválida de IA: {ai_response}")
            raise ValueError("Respuesta inválida del servicio de IA")
        
        if "study_plan" not in ai_response["data"]:
            logger.error(f"Falta campo 'study_plan' en data: {ai_response['data']}")
            raise ValueError("El plan de estudio no fue generado correctamente")
        
        ai_response_data = ai_response["data"]["study_plan"]
        logger.info(f"Plan de estudio extraído correctamente: {list(ai_response_data.keys())}")
        
        study_plan = plan_services.create_study_plan(
            title=f"Plan de estudio - {level.capitalize()}",
            level=level,
            content=ai_response_data,
            user_id=user_id,
            document_id=document.id
        )
        
        logger.info(f"Plan de estudio {study_plan.id} creado exitosamente")
        
        return study_plan
            
    except ValueError as ve:
        logger.error(f"Error de validación: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except ConnectionError as ce:
        logger.error(f"Error de conexión con IA: {ce}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de IA no disponible temporalmente"
        )
    except Exception as e:
        logger.error(f"Error inesperado en create_study_plan: {e}")
        logger.error(f"Traceback completo:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
        
        
@router.get("/{plan_id}", status_code=status.HTTP_200_OK)
def get_study_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    plan_services = StudyPlanService(db)
    
    try:
        study_plan = plan_services.get_study_plan_by_id(plan_id)
        if not study_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan de estudio no encontrado"
            )
        
        return study_plan
    
    except Exception as e:
        logger.error(f"Error inesperado en get_study_plan: {e}")
        logger.error(f"Traceback completo:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
        
@router.get("/by-document/{document_id}/{level}", status_code=status.HTTP_200_OK)
async def get_study_plan_by_document(
    document_id: int,
    level: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    plan_services = StudyPlanService(db)
    
    try:
        study_plans = plan_services.get_study_plans_by_document(document_id, level)
        return study_plans
    
    except Exception as e:
        logger.error(f"Error inesperado en get_study_plan_by_document: {e}")
        logger.error(f"Traceback completo:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )