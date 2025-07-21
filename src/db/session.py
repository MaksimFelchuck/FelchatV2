import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Подключение к PostgreSQL через переменную окружения
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://felchat:felchat@localhost:5432/felchat"
)

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_timeout=60,
    pool_recycle=3600,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)