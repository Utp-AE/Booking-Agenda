# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    # Valor por defecto (puede ser @db o tu IP fija, como prefieras):
    "postgresql+psycopg2://meeting_user:meeting_pass@db:5432/meeting_db"
    # o, si quieres que el fallback use tu IP fija:
    # "postgresql+psycopg2://meeting_user:meeting_pass@172.30.0.100:5432/meeting_db"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# Dependencia para FastAPI
def get_db():
    db = SessionLocal()   # <- aquí creas la sesión
    try:
        yield db
    finally:
        db.close()