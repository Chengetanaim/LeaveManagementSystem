from sqlalchemy import create_engine  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore

from decouple import config  # type: ignore


SQLALCHEMY_DATABASE_URL = f"postgresql://{config('DB_USERNAME')}:{config('DB_PASSWORD')}@{config('DB_HOSTNAME')}:{config('DB_PORT')}/{config('DB_NAME')}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
