
from App.services.pdf_extract import PDFExtractor
from App.services.open_ai import OpenAIClient
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import json

load_dotenv()

# Agregar ruta para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("Uso: python main.py <archivo.pdf>")
        return
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"❌ Archivo no encontrado: {pdf_path}")
        return
    
    # 1. Extraer texto del PDF
    print(f"📄 Extrayendo texto de {Path(pdf_path).name}...")
    extractor = PDFExtractor()
    text, error, metadata = extractor.extract_text(pdf_path)
    
    if error:
        print(f"❌ Error: {error}")
        return
    
    print(f"✅ Texto extraído: {len(text)} caracteres")
    
    # 2. Verificar API key de OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY no configurada - Solo extracción")
        # Guardar solo el texto extraído
        with open("texto_extraido.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print("💾 Texto guardado en: texto_extraido.txt")
        return
    
    # 3. Enviar a OpenAI
    print("🤖 Enviando a OpenAI...")
    client = OpenAIClient()
    analysis, usage = client.analyze_text(text, metadata)
    
    if not analysis:
        print(f"❌ Error en análisis: {usage.get('error')}")
        return
    
    print("✅ Análisis completado!")
    
    # 4. GUARDAR EL ANÁLISIS EN ARCHIVOS
    base_name = Path(pdf_path).stem
    
    # Guardar análisis completo en archivo de texto
    analysis_filename = f"{base_name}_analisis.txt"
    with open(analysis_filename, "w", encoding="utf-8") as f:
        f.write(f"Análisis del documento: {pdf_path}\n")
        f.write("=" * 50 + "\n\n")
        f.write(analysis)
        f.write("\n\n" + "=" * 50 + "\n")
        f.write(f"Tokens usados: {usage.get('total_tokens', 'N/A')}\n")
    
    print(f"💾 Análisis guardado en: {analysis_filename}")
    
    # Guardar metadata y uso en JSON
    json_filename = f"{base_name}_metadata.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump({
            "pdf_metadata": metadata,
            "openai_usage": usage,
            "text_length": len(text)
        }, f, indent=2, ensure_ascii=False)
    
    print(f"📊 Metadata guardada en: {json_filename}")
    
    # 5. MOSTRAR EL ANÁLISIS EN PANTALLA
    print("\n" + "🔍" * 20)
    print("📖 VISTA PREVIA DEL ANÁLISIS:")
    print("🔍" * 20)
    
    # Mostrar las primeras líneas del análisis
    lines = analysis.split('\n')
    for i, line in enumerate(lines[:15]):  # Primeras 15 líneas
        if line.strip():  # Solo mostrar líneas con contenido
            print(line)
    
    print("\n" + "📋" * 20)
    print("💡 Para ver el análisis completo:")
    print(f"   Abre el archivo: {analysis_filename}")
    print("📋" * 20)
    
    # 6. Mostrar estadísticas
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   • Tokens usados: {usage.get('total_tokens', 'N/A')}")
    print(f"   • Tiempo de respuesta: {usage.get('response_time', 'N/A'):.2f}s")
    print(f"   • Longitud del análisis: {len(analysis)} caracteres")

if __name__ == "__main__":
    main()