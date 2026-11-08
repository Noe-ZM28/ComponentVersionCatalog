from sqlalchemy import select
from app.models.change import Change

def test_add_multiple_changes_assigns_consecutive_numbers(
    client, project_factory, component_factory, ticket_factory
):
    project = project_factory()
    component = component_factory(project.id, cadena="API", step=4)
    ticket = ticket_factory(project.id)

    response = client.post(
        f"/tickets/{ticket.id}",
        json=[
            {
                "component_id": component.id,
                "title": "Cambio A",
                "description": "Descripción A",
            },
            {
                "component_id": component.id,
                "title": "Cambio B",
                "description": "Descripción B",
            },
        ],
    )

    assert response.status_code == 200
    assert [change["change_number"] for change in response.json()["changes"]] == [1, 2]
    assert all(change["cadena"] == "API" for change in response.json()["changes"])


def test_add_changes_rejects_empty_list(client, project_factory, ticket_factory):
    project = project_factory()
    ticket = ticket_factory(project.id)

    response = client.post(f"/tickets/{ticket.id}", json=[])

    assert response.status_code == 400


def test_add_changes_to_missing_ticket_returns_not_found(client):
    response = client.post(
        "/tickets/9999",
        json=[{"component_id": 1, "title": "Cambio", "description": "Descripción"}],
    )

    assert response.status_code == 404


def test_add_change_from_another_project_is_rejected(
    client, project_factory, component_factory, ticket_factory
):
    project_a = project_factory(name="Proyecto A")
    project_b = project_factory(name="Proyecto B")
    component_b = component_factory(project_b.id)
    ticket = ticket_factory(project_a.id)

    response = client.post(
        f"/tickets/{ticket.id}",
        json=[
            {
                "component_id": component_b.id,
                "title": "Cambio ajeno",
                "description": "Debe rechazarse",
            }
        ],
    )

    assert response.status_code == 404


def test_update_change_fields_without_moving_component(
    client, project_factory, component_factory, ticket_factory
):
    project = project_factory()
    component = component_factory(project.id, cadena="PAY", step=9)
    ticket = ticket_factory(project.id, components=[(component, 1)])
    change_id = ticket.changes[0].id

    response = client.patch(
        f"/change/{change_id}",
        json={"title": "Título actualizado", "description": "Descripción actualizada"},
    )

    assert response.status_code == 200
    change = response.json()
    assert change["title"] == "Título actualizado"
    assert change["description"] == "Descripción actualizada"
    assert (change["component_id"], change["change_number"], change["cadena"], change["step"]) == (
        component.id,
        1,
        "PAY",
        9,
    )


def test_update_change_without_changes_returns_bad_request(
    client, project_factory, component_factory, ticket_factory
):
    project = project_factory()
    component = component_factory(project.id)
    ticket = ticket_factory(project.id, components=[(component, 1)])

    response = client.patch(
        f"/change/{ticket.changes[0].id}",
        json={"title": ticket.changes[0].title},
    )

    assert response.status_code == 400


def test_reassign_change_preserves_history_and_assigns_next_number(
    client, project_factory, component_factory, ticket_factory, session_factory
):
    project = project_factory()

    source = component_factory(
        project.id, name="Origen", cadena="SRC", step=1
    )
    destination = component_factory(
        project.id, name="Destino", cadena="DST", step=2
    )

    ticket_a = ticket_factory(
        project.id,
        ticket_key="MOVE-1",
        components=[(source, 1), (source, 2)],
    )
    ticket_b = ticket_factory(
        project.id,
        ticket_key="MOVE-2",
        components=[(destination, 1)],
    )

    moving_change_id = ticket_a.changes[0].id
    remaining_change_id = ticket_a.changes[1].id
    original_ticket_id = ticket_a.id

    response = client.patch(
        f"/change/{moving_change_id}",
        json={"component_id": destination.id},
    )

    assert response.status_code == 200

    # Consultar desde una sesión nueva para evitar relaciones desactualizadas.
    with session_factory() as session:
        moving_change = session.get(Change, moving_change_id)
        remaining_change = session.get(Change, remaining_change_id)

        assert moving_change is not None
        assert remaining_change is not None

        # El cambio conserva su ticket original.
        assert moving_change.ticket_id == original_ticket_id

        # El cambio ahora pertenece al componente destino.
        assert moving_change.component_id == destination.id
        assert moving_change.change_number == 2
        assert moving_change.cadena == "DST"
        assert moving_change.step == 2

        # El cambio restante conserva su componente y numeración.
        assert remaining_change.component_id == source.id
        assert remaining_change.change_number == 2
        assert remaining_change.cadena == "SRC"
        assert remaining_change.step == 1

        # El cambio previo del destino no se modifica.
        destination_changes = session.scalars(
            select(Change)
            .where(Change.component_id == destination.id)
            .order_by(Change.change_number)
        ).all()

        assert [change.change_number for change in destination_changes] == [1, 2]


def test_reassign_change_rejects_other_project_and_missing_component(
    client, project_factory, component_factory, ticket_factory
):
    project_a = project_factory(name="Proyecto A")
    project_b = project_factory(name="Proyecto B")
    source = component_factory(project_a.id)
    foreign = component_factory(project_b.id)
    ticket = ticket_factory(project_a.id, components=[(source, 1)])

    foreign_response = client.patch(
        f"/change/{ticket.changes[0].id}",
        json={"component_id": foreign.id},
    )
    missing_response = client.patch(
        f"/change/{ticket.changes[0].id}",
        json={"component_id": 9999},
    )

    assert foreign_response.status_code == 400
    assert missing_response.status_code == 404


def test_update_missing_change_returns_not_found(client):
    response = client.patch("/change/9999", json={"title": "No existe"})

    assert response.status_code == 404

def test_add_multiple_changes_rolls_back_all_if_one_component_is_invalid(
    client, project_factory, component_factory, ticket_factory, session_factory
):
    project = project_factory()
    component = component_factory(project.id)
    ticket = ticket_factory(project.id)

    response = client.post(
        f"/tickets/{ticket.id}",
        json=[
            {
                "component_id": component.id,
                "title": "Cambio válido",
                "description": "Este cambio no debe guardarse",
            },
            {
                "component_id": 9999,
                "title": "Cambio inválido",
                "description": "El componente no existe",
            },
        ],
    )

    assert response.status_code == 404

    # Comprobar desde una sesión nueva que no se guardó ninguno.
    with session_factory() as session:
        saved_changes = session.scalars(
            select(Change).where(Change.ticket_id == ticket.id)
        ).all()

        assert saved_changes == []