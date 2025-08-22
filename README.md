# 📚 Asistente de Estudio con IA

El **Asistente de Estudio con IA** es una aplicación diseñada para ayudar a los estudiantes a optimizar su tiempo de aprendizaje.  
Permite **subir documentos (PDF, Word, TXT)** y obtener **resúmenes automáticos, preguntas de repaso y quizzes interactivos**, además de la opción de escuchar el contenido en audio con **Text-to-Speech**.

---

## 🚀 Tecnologías utilizadas

### 🎨 Frontend
- **Angular** → Aplicación web para gestión de documentos, resúmenes y quizzes.  
- **Flutter** → Aplicación móvil para acceder al asistente desde cualquier dispositivo.  

### ⚙️ Backend
- **FastAPI** → Framework de Python para construir la API REST.  
- **API (OPENIA)** → Procesamiento de lenguaje natural para resúmenes y generación de preguntas.  
- **gTTS / pyttsx3** → Text-to-Speech para convertir texto en audio.  

### 🗄️ Base de Datos
- **PostgreSQL** → Almacenamiento de usuarios, documentos y resultados de quizzes.  
- **SQLAlchemy + Alembic** → ORM y migraciones de la base de datos.  

---


## ⚡ Instalación y ejecución

### 🔹 Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Accede a la documentación interactiva de la API en:
👉 http://127.0.0.1:8000/docs

### 🔹 Frontend (Angular)
```bash
cd frontend-angular
npm install
ng serve
```

Accede a: http://localhost:4200

### 🔹 Móvil (Flutter)

```bash
cd mobile-flutter
flutter pub get
flutter run
```

### 🛠️ Dependencias principales
- FastAPI, SQLAlchemy, Alembic → Backend y base de datos.

- PyPDF2, pdfplumber → Extracción de texto de documentos.

- Spacy, NLTK, HuggingFace Transformers → NLP y generación de resúmenes.

- gTTS, pyttsx3 → Text-to-Speech.

- Angular, Flutter → Interfaz web y móvil.

- PostgreSQL → Base de datos relacional.

### 👨‍💻 Equipo de desarrollo

-**Product Owner**: Eduardo Andres Solano Rodriguez

-**Scrum Master**: Eduardo Andres Solano Rodriguez

-**Equipo Dev**: Desarrollo frontend, backend e IA.



### 📄 Licencia
Este proyecto es académico y desarrollado como parte del curso de Ingeniería de Sistemas – 7° semestre.