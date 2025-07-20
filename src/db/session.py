import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Подключение к PostgreSQL через переменную окружения
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://felchat:felchat@localhost:5432/felchat"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
