from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from App.Models.models import CustomStudyPlan, Document, User

class StudyPlanService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_study_plan(
        self,
        title: str,
        level: str,
        content: dict,
        user_id: int,
        document_id: Optional[int] = None
    ) -> CustomStudyPlan:
        """
        Crea un nuevo plan de estudio personalizado.
        
        Args:
            title: Título del plan de estudio
            level: Nivel del plan (básico, intermedio, avanzado)
            content: Diccionario con la estructura del plan
            user_id: ID del usuario que crea el plan
            document_id: ID del documento relacionado (opcional)
        
        Returns:
            El plan de estudio creado
        """
        # Validar que el usuario existe
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # Validar que el documento existe si se proporciona
        if document_id:
            document = self.db.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise ValueError("Documento no encontrado")
        
        # Crear el plan de estudio
        study_plan = CustomStudyPlan(
            title=title,
            level=level.lower(),
            content=content,
            user_id=user_id,
            document_id=document_id,
        )
        
        self.db.add(study_plan)
        self.db.commit()
        self.db.refresh(study_plan)
        
        return study_plan
    
    def get_study_plan_by_id(self, plan_id: int) -> Optional[CustomStudyPlan]:
        """
        Obtiene un plan de estudio por su ID.
        
        Args:
            plan_id: ID del plan de estudio
        
        Returns:
            El plan de estudio o None si no existe
        """
        return self.db.query(CustomStudyPlan).filter(
            CustomStudyPlan.id == plan_id
        ).first()
    
    def get_study_plans_by_user(
        self,
        user_id: int,
        active_only: bool = True
    ) -> List[CustomStudyPlan]:
        """
        Obtiene todos los planes de estudio de un usuario.
        
        Args:
            user_id: ID del usuario
            active_only: Si es True, solo devuelve planes activos
        
        Returns:
            Lista de planes de estudio
        """
        query = self.db.query(CustomStudyPlan).filter(
            CustomStudyPlan.user_id == user_id
        )
        
        
        return query.order_by(CustomStudyPlan.created_at.desc()).all()
    
    def get_study_plans_by_document(
        self,
        document_id: int,
        user_id: Optional[int] = None
    ) -> List[CustomStudyPlan]:
        """
        Obtiene todos los planes de estudio relacionados con un documento.
        
        Args:
            document_id: ID del documento
            user_id: ID del usuario (opcional, para filtrar por usuario)
        
        Returns:
            Lista de planes de estudio
        """
        query = self.db.query(CustomStudyPlan).filter(
            CustomStudyPlan.document_id == document_id
        )
        
        if user_id:
            query = query.filter(CustomStudyPlan.user_id == user_id)
        
        return query.order_by(CustomStudyPlan.created_at.desc()).all()
    
    
    def get_study_plans_by_level(
        self,
        level: str,
        user_id: Optional[int] = None
    ) -> List[CustomStudyPlan]:
        """
        Obtiene planes de estudio filtrados por nivel.
        
        Args:
            level: Nivel a filtrar (básico, intermedio, avanzado)
            user_id: ID del usuario (opcional)
        
        Returns:
            Lista de planes de estudio
        """
        query = self.db.query(CustomStudyPlan).filter(
            CustomStudyPlan.level == level.lower()
        )
        
        if user_id:
            query = query.filter(CustomStudyPlan.user_id == user_id)
        
        return query.order_by(CustomStudyPlan.created_at.desc()).all()
    
    def activate_study_plan(self, plan_id: int) -> CustomStudyPlan:
        """
        Activa un plan de estudio previamente desactivado.
        
        Args:
            plan_id: ID del plan de estudio
        
        Returns:
            El plan de estudio activado
        """
        return self.update_study_plan(plan_id, is_active=True)
    
    def deactivate_study_plan(self, plan_id: int) -> CustomStudyPlan:
        """
        Desactiva un plan de estudio.
        
        Args:
            plan_id: ID del plan de estudio
        
        Returns:
            El plan de estudio desactivado
        """
        return self.update_study_plan(plan_id, is_active=False)
