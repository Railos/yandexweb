from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import os

# Путь к базе данных (папка db/users.db)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "users.db")

# Настройка подключения к SQLite
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Создаём движок SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Для работы в многопоточном режиме
    echo=True  # Логирование SQL-запросов (можно отключить в продакшене)
)

# Фабрика сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Для работы в Flask (scoped_session)
db_session = scoped_session(SessionLocal)

# Базовый класс для моделей
SqlAlchemyBase = declarative_base()

from . import all_models

def init_db():
    SqlAlchemyBase.metadata.create_all(bind=engine)

def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()