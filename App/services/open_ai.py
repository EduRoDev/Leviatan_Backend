import logging
from typing import Dict, Any, Optional, Tuple
import time
from openai import OpenAI
from App.Core.config import settings

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        logger.info("Cliente inicizalizado con OpenAI")

    def analyze_text(self, text: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Analiza el texto utilizando el modelo de OpenAI para generar un resumen, flashcards
        y un quiz basado en el contenido del texto.
        """
        try:
            prompt = self._create_analysis_prompt(text)
            logger.info("Enviando solicitud al modelo de OpenAI")
            start_time = time.time()
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente experto y util que ayuda a analizar y resumir documentos, crear flashcards de estudio y quizzes."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            end_time = time.time()
            content= response.choices[0].message.content
            usage = response.usage
            logger.info(f"Análisis completado en {end_time - start_time:.2f}s")
            
            return content,{
                "model": settings.OPENAI_MODEL,
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "response_time": end_time - start_time
            }
        except Exception as e:
            logger.error(f"Error al analizar el texto: {e}")
            return None, {"error": str(e)}


    def _create_analysis_prompt(self, text: str) -> str:
        max_length = 10000
        truncated_text = text[:max_length] + "..." if len(text) > max_length else text
        
        return f"""
        ANALIZA el siguiente texto y devuelve EXCLUSIVAMENTE un JSON válido con esta estructura exacta:

        {{
            "summary": "resumen completo del documento aquí",
            "flashcards": [
                {{
                    "subject": "tema específico 1",
                    "definition": "definición detallada 1"
                }},
                {{
                    "subject": "tema específico 2", 
                    "definition": "definición detallada 2"
                }}
            ],
            "quiz": {{
                "title": "título del quiz basado en el documento",
                "questions": [
                    {{
                        "question_text": "pregunta 1 aquí",
                        "options": ["Opción A", "Opción B", "Opción C", "Opción D"],
                        "correct_option": "Opción correcta"
                    }},
                    {{
                        "question_text": "pregunta 2 aquí",
                        "options": ["Opción A", "Opción B", "Opción C", "Opción D"],
                        "correct_option": "Opción correcta" 
                    }}
                ]
            }}
        }}

        TEXTO A ANALIZAR:
        {truncated_text}

        IMPORTANTE: Devuelve SOLO el JSON válido, sin texto adicional, sin ```json, ni explicaciones.
        """