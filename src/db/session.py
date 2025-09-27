from src.db.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core import get_settings

db_host = get_settings().POSTGRES_HOST
db_port = get_settings().POSTGRES_PORT
db_name = get_settings().POSTGRES_DB
db_user = get_settings().POSTGRES_USER
db_password = get_settings().POSTGRES_PASSWORD
db_driver = get_settings().DB_DRIVER

DATABASE_URL = f"{db_driver}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()