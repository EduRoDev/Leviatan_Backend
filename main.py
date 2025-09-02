from App.Database.init_db import init
from App.Services.pdf_extract import pdf_extractor
from App.Services.open_ai import OpenAIClient
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import json
from App.Services.document_services import DocumentService
from App.Database.database import SessionLocal
from App.Services.summary_services import SummaryService


load_dotenv()


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def db_init():
    init.create_tables()

def test_save_document():
    db = SessionLocal()
    service = DocumentService(db)
    project_root = Path(__file__).parent
    file_path = project_root / "Files" / "oratoria.pdf"

    service.save_document(file_path=file_path)
    
    saved = service.get_document(1)
    client = OpenAIClient()
    
    content, metadata = client.analyze_text(saved.content)
    
    print("Contenido:", content)
    print("Metadata:", metadata)

    if content:  
        try:
            parsed = json.loads(content)
            print("JSON parseado correctamente:", parsed)
            
            summary_text = parsed.get("summary")
            
            if summary_text:
                summary_service = SummaryService(db)
                summary_service.save_summary(content=summary_text, document_id=saved.id)
                print("Resumen guardado en la base de datos.")

                summary_saved = summary_service.get_summary(1)
                print(summary_saved.content)
            else:
                print("No se encontró 'summary' en la respuesta")
                
        except json.JSONDecodeError as e:
            print(f"Error al parsear JSON: {e}")
            print(f"Contenido recibido: {content}")
        except Exception as e:
            print(f"Error inesperado: {e}")
    else:
        print("No se recibió contenido de OpenAI")

    db.close()    

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <archivo.pdf>")
        return
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"❌ Archivo no encontrado: {pdf_path}")
        return
    
    print(f"📄 Extrayendo texto de {Path(pdf_path).name}...")
    extractor = pdf_extractor
    text, error, metadata = extractor.extract_text(pdf_path)
    
    if error:
        print(f"❌ Error: {error}")
        return
    
    print(f"✅ Texto extraído: {len(text)} caracteres")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY no configurada - Solo extracción")
        with open("texto_extraido.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print("💾 Texto guardado en: texto_extraido.txt")
        return
    
    print("🤖 Enviando a OpenAI...")
    client = OpenAIClient()
    analysis, usage = client.analyze_text(text, metadata)
    
    if not analysis:
        print(f"❌ Error en análisis: {usage.get('error')}")
        return
    
    print("✅ Análisis completado!")
    
    base_name = Path(pdf_path).stem
    
    analysis_filename = f"{base_name}_analisis.txt"
    with open(analysis_filename, "w", encoding="utf-8") as f:
        f.write(f"Análisis del documento: {pdf_path}\n")
        f.write("=" * 50 + "\n\n")
        f.write(analysis)
        f.write("\n\n" + "=" * 50 + "\n")
        f.write(f"Tokens usados: {usage.get('total_tokens', 'N/A')}\n")
    
    print(f"💾 Análisis guardado en: {analysis_filename}")
    
    json_filename = f"{base_name}_metadata.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump({
            "pdf_metadata": metadata,
            "openai_usage": usage,
            "text_length": len(text)
        }, f, indent=2, ensure_ascii=False)
    
    print(f"📊 Metadata guardada en: {json_filename}")
    
    print("\n" + "🔍" * 20)
    print("📖 VISTA PREVIA DEL ANÁLISIS:")
    print("🔍" * 20)
    
    lines = analysis.split('\n')
    for i, line in enumerate(lines[:15]): 
        if line.strip():  
            print(line)
    
    print("\n" + "📋" * 20)
    print("💡 Para ver el análisis completo:")
    print(f"   Abre el archivo: {analysis_filename}")
    print("📋" * 20)
    
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   • Tokens usados: {usage.get('total_tokens', 'N/A')}")
    print(f"   • Tiempo de respuesta: {usage.get('response_time', 'N/A'):.2f}s")
    print(f"   • Longitud del análisis: {len(analysis)} caracteres")

if __name__ == "__main__":
    # db_init()
    # main()
    test_save_document()