from app.database import Base, engine
from app.models import (
    Project,
    Component,
    Ticket,
    Change,
    FileRecord,
    ChangeFile,
)


def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("Base de datos inicializada correctamente.")
    print(f"Tablas creadas: {', '.join(Base.metadata.tables.keys())}")


if __name__ == "__main__":
    initialize_database()