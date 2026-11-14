import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.models.change import Change
from app.models.change_file import ChangeFile
from app.models.component import Component
from app.models.file_record import FileRecord
from app.models.project import Project
from app.models.ticket import Ticket
from app.services.catalog_seed import seed_catalog


def test_component_name_is_unique_per_project(db_session, project_factory, component_factory):
    project = project_factory()
    component_factory(project.id, name="Nombre único")
    duplicate = Component(
        project_id=project.id,
        name="Nombre único",
        description="Duplicado",
    )
    db_session.add(duplicate)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_change_number_is_unique_per_component(
    db_session, project_factory, component_factory, ticket_factory
):
    project = project_factory()
    component = component_factory(project.id)
    ticket = ticket_factory(project.id, components=[(component, 1)])
    duplicate_ticket = Ticket(
        project_id=project.id,
        ticket_key="INTEGRITY-2",
        title="Duplicado",
        description="Duplicado",
        ticket_url="https://example.com/INTEGRITY-2",
    )
    db_session.add(duplicate_ticket)
    db_session.flush()
    db_session.add(
        Change(
            project_id=project.id,
            component_id=component.id,
            ticket_id=duplicate_ticket.id,
            change_number=1,
            title="Duplicado",
            description="Número repetido",
            step=component.step,
        )
    )

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_file_relationships_are_created_with_upload(
    client, db_session, project_factory, component_factory, ticket_factory
):
    import json

    project = project_factory()
    component = component_factory(project.id)
    ticket = ticket_factory(project.id, components=[(component, 1)])
    change = ticket.changes[0]

    response = client.post(
        f"/projects/{project.id}/changes/{change.id}/files/uploadfiles",
        data={
            "metadata": json.dumps(
                [
                    {
                        "type_file": "source",
                        "role": "before",
                        "description": "Versión anterior",
                    }
                ]
            )
        },
        files=[("files", ("source.txt", b"old content", "text/plain"))],
    )

    assert response.status_code == 200
    file_record = db_session.scalar(select(FileRecord))
    association = db_session.scalar(select(ChangeFile))
    assert file_record is not None
    assert association is not None
    assert association.change_id == change.id
    assert association.file_id == file_record.id


def test_demo_seed_keeps_foreign_keys_chains_steps_and_change_numbers_valid(db_session):
    result = seed_catalog(db_session)

    assert 1 <= result["generated_changes"] <= 15
    seeded_projects = db_session.scalars(select(Project)).all()
    assert seeded_projects
    assert all(project.name not in {"Proyecto 1", "Proyecto 2"} for project in seeded_projects)
    assert all(
        project.cust_num is not None and 100 <= project.cust_num <= 999
        for project in seeded_projects
    )

    invalid_changes = db_session.scalar(
        select(func.count())
        .select_from(Change)
        .join(Ticket, Change.ticket_id == Ticket.id)
        .join(Component, Change.component_id == Component.id)
        .where(
            (Change.project_id != Ticket.project_id)
            | (Change.project_id != Component.project_id)
        )
    )
    duplicate_numbers = db_session.execute(
        select(Change.component_id, Change.change_number)
        .group_by(Change.component_id, Change.change_number)
        .having(func.count() > 1)
    ).all()
    assert invalid_changes == 0
    assert duplicate_numbers == []

    generated_components = db_session.scalars(
        select(Component).where(Component.name.like("% - % %"))
    ).all()
    assert all(1 <= component.step <= 25 for component in generated_components)
    assert all(
        component.type_component.value
        in {"PC1", "Reporte", "Carrier", "API", "Batch", "Seguridad", "other"}
        for component in generated_components
    )
