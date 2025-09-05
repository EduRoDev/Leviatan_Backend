from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from App.Core.config import settings

DATABASE_URL = f"postgresql+psycopg2://{settings.USER_DB}:{settings.USER_DB_PASSWORD}@localhost:5432/{settings.DB_NAME}"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



