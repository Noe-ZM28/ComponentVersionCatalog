from sqlalchemy import inspect, text

from app.database import Base, engine
from app.models import (
    Project,
    Component,
    Ticket,
    Change,
    FileRecord,
    ChangeFile,
)


def migrate_project_cust_num(database_engine=engine):
    inspector = inspect(database_engine)
    if inspector.has_table("projects") and "cust_num" not in {
        column["name"] for column in inspector.get_columns("projects")
    }:
        with database_engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE projects ADD cust_num INTEGER NULL")
            )


def initialize_database():
    migrate_project_cust_num()
    Base.metadata.create_all(bind=engine)
    print("Base de datos inicializada correctamente.")
    print(f"Tablas creadas: {', '.join(Base.metadata.tables.keys())}")


if __name__ == "__main__":
    initialize_database()