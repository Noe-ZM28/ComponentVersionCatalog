from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

external_engine = None
ExternalSessionLocal = None

if settings.external_database_url:
    external_engine = create_engine(
        settings.external_database_url,
        pool_pre_ping=True,
    )

    ExternalSessionLocal = sessionmaker(
        bind=external_engine,
        autoflush=False,
        autocommit=False,
    )


class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_external_db():
    if ExternalSessionLocal is None:
        raise RuntimeError(
            "La conexión externa no está configurada. "
            "Verifica EXTERNAL_DATABASE_URL en el archivo .env."
        )

    db = ExternalSessionLocal()
    try:
        yield db
    finally:
        db.close()
