import logging
from typing import Dict, Any, Optional, Tuple, List
import time
import asyncio
import json
from openai import AsyncOpenAI
from openai import APIError, RateLimitError, APIConnectionError, APITimeoutError
from App.Core.config import settings

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self):
        # Validar configuración antes de crear el cliente
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY no está configurada")
        
        if not hasattr(settings, 'OPENAI_MODEL') or not settings.OPENAI_MODEL:
            raise ValueError("OPENAI_MODEL no está configurado")
        
        # Configurar cliente con parámetros opcionales
        client_kwargs = {
            "api_key": settings.OPENAI_API_KEY,
            "timeout": 60.0  # Timeout por defecto de 60 segundos
        }
        
        # Configurar base_url (siempre necesario para OpenRouter)
        if hasattr(settings, 'OPENAI_BASE_URL') and settings.OPENAI_BASE_URL:
            client_kwargs["base_url"] = settings.OPENAI_BASE_URL
            
        # Headers adicionales para OpenRouter
        if settings.is_openrouter():
            extra_headers = settings.get_client_headers()
            if extra_headers:
                client_kwargs["default_headers"] = extra_headers
            
        self.client = AsyncOpenAI(**client_kwargs)
        provider = "OpenRouter" if settings.is_openrouter() else "OpenAI"
        logger.info(f"Cliente Async de {provider} inicializado con modelo: {settings.OPENAI_MODEL}")

    

    async def analyze_text_parallel(self, text: str) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Analiza el texto utilizando llamadas paralelas a OpenAI para cada componente
        """
        try:
            # Probar conexión antes de procesar
            if not await self.test_connection():
                error_msg = "No se pudo establecer conexión con OpenAI"
                logger.error(error_msg)
                return None, {"error": error_msg}
            
            max_length = 10000
            truncated_text = text[:max_length] + "..." if len(text) > max_length else text
            
            tasks = [
                self._generate_summary(truncated_text),
                self._generate_flashcards(truncated_text),
                self._generate_quiz(truncated_text)
            ]
            
            logger.info("Iniciando llamadas paralelas a OpenAI")
            start_time = time.time()
            
            # Usar timeout para el gather
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=120.0  # 2 minutos total
                )
            except asyncio.TimeoutError:
                logger.error("Timeout en llamadas paralelas a OpenAI")
                return None, {"error": "Timeout en procesamiento"}
            
            end_time = time.time()
            total_time = end_time - start_time
            
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error en tarea {i}: {result}")
                    return None, {"error": f"Error en procesamiento: {result}"}
                processed_results.append(result)
            
            summary_result, flashcards_result, quiz_result = processed_results
            
            if not all([
                summary_result and "content" in summary_result,
                flashcards_result and "flashcards" in flashcards_result,
                quiz_result and "quiz" in quiz_result
            ]):
                logger.error("Estructura de respuesta inválida de OpenAI")
                return None, {"error": "Estructura de respuesta inválida de la API"}
            
            combined_result = {
                "summary": summary_result["content"],
                "flashcards": flashcards_result["flashcards"],
                "quiz": quiz_result["quiz"]
            }
            
            combined_meta = {
                "model": settings.OPENAI_MODEL,
                "prompt_tokens": sum(r.get("usage", {}).get("prompt_tokens", 0) for r in processed_results),
                "completion_tokens": sum(r.get("usage", {}).get("completion_tokens", 0) for r in processed_results),
                "total_tokens": sum(r.get("usage", {}).get("total_tokens", 0) for r in processed_results),
                "response_time": total_time,
                "individual_times": {
                    "summary": processed_results[0].get("response_time", 0),
                    "flashcards": processed_results[1].get("response_time", 0),
                    "quiz": processed_results[2].get("response_time", 0)
                }
            }
            
            logger.info(f"✅ Análisis paralelo completado en {total_time:.2f}s")
            return combined_result, combined_meta
            
        except Exception as e:
            logger.error(f"Error en análisis paralelo: {e}")
            return None, {"error": str(e)}

    async def _generate_summary(self, text: str) -> Dict[str, Any]:
        """Genera solo el resumen"""
        try:
            prompt = f"""
            Genera un resumen completo y conciso del siguiente texto. 
            Devuelve SOLO un JSON con esta estructura:
            {{"summary": "resumen completo aquí"}}
            
            TEXTO:
            {text}
            
            IMPORTANTE: Devuelve SOLO el JSON válido, sin texto adicional.
            """
            
            start_time = time.time()
            
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Eres un experto en resumir documentos académicos. Devuelve solo JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
                timeout=45.0
            )
            
            end_time = time.time()
            
            if not response.choices or not response.choices[0].message.content:
                raise ValueError("Respuesta vacía de OpenAI")
            
            content_str = response.choices[0].message.content.strip()
            
            if content_str.startswith('```json'):
                content_str = content_str.replace('```json', '').replace('```', '').strip()
            
            content = json.loads(content_str)
            
            if "summary" not in content:
                raise ValueError("Estructura JSON inválida: falta campo 'summary'")
            
            logger.info("✅ Resumen generado exitosamente")
            return {
                "content": content["summary"],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "response_time": end_time - start_time
            }
            
        except APIConnectionError as e:
            error_msg = f"Error de conexión generando resumen: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)
        except APITimeoutError as e:
            error_msg = f"Timeout generando resumen: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)
        except RateLimitError as e:
            error_msg = f"Rate limit excedido generando resumen: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)
        except APIError as e:
            error_msg = f"Error de API generando resumen: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)
        except json.JSONDecodeError as e:
            error_msg = f"Error decodificando JSON del resumen: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            logger.error(f"Error generando resumen: {e}")
            raise

    async def _generate_flashcards(self, text: str) -> Dict[str, Any]:
        """Genera solo las flashcards"""
        try:
            prompt = f"""
            Crea EXACTAMENTE 5 flashcards de estudio basadas en el texto.
            Devuelve SOLO un JSON con esta estructura:
            {{
                "flashcards": [
                    {{"subject": "tema 1", "definition": "definición 1"}},
                    {{"subject": "tema 2", "definition": "definición 2"}}
                ]
            }}
            
            TEXTO:
            {text}
            
            IMPORTANTE: Devuelve SOLO el JSON válido, sin texto adicional.
            """
            
            start_time = time.time()
            
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Eres un experto en crear flashcards educativas. Devuelve solo JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
                timeout=45.0
            )
            
            end_time = time.time()
            
            if not response.choices or not response.choices[0].message.content:
                raise ValueError("Respuesta vacía de OpenAI")
            
            content_str = response.choices[0].message.content.strip()
            if content_str.startswith('```json'):
                content_str = content_str.replace('```json', '').replace('```', '').strip()
            
            content = json.loads(content_str)
            
            if "flashcards" not in content or not isinstance(content["flashcards"], list):
                raise ValueError("Estructura JSON inválida: falta campo 'flashcards' o no es una lista")
            
            logger.info("✅ Flashcards generadas exitosamente")
            return {
                "flashcards": content["flashcards"],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "response_time": end_time - start_time
            }
            
        except APIConnectionError as e:
            error_msg = f"Error de conexión generando flashcards: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)
        except APITimeoutError as e:
            error_msg = f"Timeout generando flashcards: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)
        except RateLimitError as e:
            error_msg = f"Rate limit excedido generando flashcards: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)
        except APIError as e:
            error_msg = f"Error de API generando flashcards: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)
        except json.JSONDecodeError as e:
            error_msg = f"Error decodificando JSON de flashcards: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            logger.error(f"Error generando flashcards: {e}")
            raise

    async def _generate_quiz(self, text: str) -> Dict[str, Any]:
        """Genera solo el quiz"""
        try:
            prompt = f"""
            Crea un quiz con MÍNIMO 5 preguntas basadas en el texto.
            Devuelve SOLO un JSON con esta estructura:
            {{
                "quiz": {{
                    "title": "título del quiz",
                    "questions": [
                        {{
                            "question_text": "pregunta 1",
                            "options": ["A", "B", "C", "D"],
                            "correct_option": "Opción correcta"
                        }}
                    ]
                }}
            }}
            
            TEXTO:
            {text}
            
            IMPORTANTE: Devuelve SOLO el JSON válido, sin texto adicional.
            """
            
            start_time = time.time()
            
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Eres un experto en crear quizzes educativos. Devuelve solo JSON válido."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
                timeout=45.0
            )
            
            end_time = time.time()
            
            if not response.choices or not response.choices[0].message.content:
                raise ValueError("Respuesta vacía de OpenAI")
            
            content_str = response.choices[0].message.content.strip()
            if content_str.startswith('```json'):
                content_str = content_str.replace('```json', '').replace('```', '').strip()
            
            content = json.loads(content_str)
            
            if "quiz" not in content or "questions" not in content["quiz"]:
                raise ValueError("Estructura JSON inválida: falta campo 'quiz' o 'questions'")
            
            logger.info("✅ Quiz generado exitosamente")
            return {
                "quiz": content["quiz"],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "response_time": end_time - start_time
            }
            
        except APIConnectionError as e:
            error_msg = f"Error de conexión generando quiz: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)
        except APITimeoutError as e:
            error_msg = f"Timeout generando quiz: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)
        except RateLimitError as e:
            error_msg = f"Rate limit excedido generando quiz: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)
        except APIError as e:
            error_msg = f"Error de API generando quiz: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)
        except json.JSONDecodeError as e:
            error_msg = f"Error decodificando JSON del quiz: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            logger.error(f"Error generando quiz: {e}")
            raise

    async def chat_with_document(
        self,
        document_content:  str,
        user_message: str,
        chat_history: List[Dict[str,str]] = None
    ) -> str:
        
        try:
            max_document_length = 8000
            truncated_content = document_content[:max_document_length] + "..." if len(document_content) > max_document_length else document_content
            system_prompt = f""" 
            Eres un asistente de educativo experto. Tu trabajo es responser las preguntas del usuario sobre el siguiente documento.
            
            DOCUMENTO:
            {truncated_content}
            
            INSTRUCCIONES:
            - Responderas ÚNICAMENTE basándote en la información del documento.
            - Si la información no está en el documento, Indicalo claramente.    
            - Se conciso y claro en tus respuestas.
            - Si te piden un resumen o una expliacion hazla en base al documento y que no pase un limite de 150 palabras.
            - Siempre mantén un tono profesional y educativo.
            """
            
            messages = [{"role": "system", "content": system_prompt}]
            
            if chat_history:
                recent_history = list(reversed(chat_history[-10:]))
                messages.extend(recent_history)
            
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            response = await self.client.chat.completions.create(
                model=settings.CHAT_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            if not response.choices or not response.choices[0].message.content:
                raise ValueError("Respuesta vacía de OpenAI")
            
            response_text = response.choices[0].message.content.strip()
            return response_text
            
        except Exception as e:
            logger.error(f"Error en chat_with_document: {e}")
            return "Lo siento, ha ocurrido un error al procesar tu solicitud."