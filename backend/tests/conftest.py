import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database import Base, get_db
from app.main import app
from app.models import Change, Component, Project, Ticket
from app.services.file_service import settings


@pytest.fixture
def test_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def session_factory(test_engine):
    return sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )


@pytest.fixture
def db_session(session_factory):
    with session_factory() as session:
        yield session


@pytest.fixture
def client(session_factory, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "storage_path", str(tmp_path / "files"))

    def override_get_db():
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def project_factory(db_session):
    def create_project(name="Proyecto de prueba", description="Proyecto de prueba"):
        project = Project(name=name, description=description)
        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)
        return project

    return create_project


@pytest.fixture
def component_factory(db_session):
    def create_component(
        project_id,
        name="Componente de prueba",
        description="Componente de prueba",
        cadena="PRD",
        step=1,
        ref_id=None,
        source_type="other",
        source_reference=None,
    ):
        component = Component(
            project_id=project_id,
            name=name,
            description=description,
            cadena=cadena,
            step=step,
            ref_id=ref_id,
            source_type=source_type,
            source_reference=source_reference,
        )
        db_session.add(component)
        db_session.commit()
        db_session.refresh(component)
        return component

    return create_component


@pytest.fixture
def ticket_factory(db_session, component_factory):
    def create_ticket(project_id, ticket_key="TEST-1", components=None):
        ticket = Ticket(
            project_id=project_id,
            ticket_key=ticket_key,
            title=f"Ticket {ticket_key}",
            description="Ticket de prueba",
            ticket_url=f"https://example.com/{ticket_key}",
        )
        db_session.add(ticket)
        db_session.flush()

        for component, change_number in components or []:
            ticket.changes.append(
                Change(
                    project_id=project_id,
                    component_id=component.id,
                    change_number=change_number,
                    title=f"Cambio {change_number}",
                    description="Cambio de prueba",
                    cadena=component.cadena,
                    step=component.step,
                )
            )

        db_session.commit()
        db_session.refresh(ticket)
        return ticket

    return create_ticket
