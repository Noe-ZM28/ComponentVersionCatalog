def test_create_ticket_creates_changes_with_component_location(
    client, project_factory, component_factory
):
    project = project_factory()
    component = component_factory(project.id, cadena="PAY", step=7)

    response = client.post(
        f"/projects/{project.id}/tickets",
        json={
            "ticket_key": "PAY-1",
            "title": "Ajuste de pagos",
            "description": "Validar autorización",
            "ticket_url": "https://example.com/PAY-1",
            "changes": [
                {
                    "component_id": component.id,
                    "title": "Primera versión",
                    "description": "Cambio inicial",
                }
            ],
        },
    )

    assert response.status_code == 201
    ticket = response.json()
    assert ticket["changes"][0]["change_number"] == 1
    assert ticket["changes"][0]["cadena"] == "PAY"
    assert ticket["changes"][0]["step"] == 7


def test_create_ticket_with_multiple_changes_same_component_numbers_consecutively(
    client, project_factory, component_factory
):
    project = project_factory()
    component = component_factory(project.id)

    response = client.post(
        f"/projects/{project.id}/tickets",
        json={
            "ticket_key": "MULTI-1",
            "title": "Cambios múltiples",
            "description": "Dos cambios para el mismo componente",
            "ticket_url": "https://example.com/MULTI-1",
            "changes": [
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
        },
    )

    assert response.status_code == 201
    assert [change["change_number"] for change in response.json()["changes"]] == [1, 2]


def test_create_duplicate_ticket_key_returns_conflict(
    client, project_factory, component_factory, ticket_factory
):
    project = project_factory()
    component = component_factory(project.id)
    ticket_factory(project.id, ticket_key="DUP-1")

    response = client.post(
        f"/projects/{project.id}/tickets",
        json={
            "ticket_key": "DUP-1",
            "title": "Duplicado",
            "description": "Duplicado",
            "ticket_url": "https://example.com/DUP-1",
            "changes": [
                {
                    "component_id": component.id,
                    "title": "Cambio",
                    "description": "Descripción",
                }
            ],
        },
    )

    assert response.status_code == 409


def test_create_ticket_rejects_component_from_another_project(
    client, project_factory, component_factory
):
    project_a = project_factory(name="Proyecto A")
    project_b = project_factory(name="Proyecto B")
    component_b = component_factory(project_b.id)

    response = client.post(
        f"/projects/{project_a.id}/tickets",
        json={
            "ticket_key": "CROSS-1",
            "title": "Cruce",
            "description": "Componente ajeno",
            "ticket_url": "https://example.com/CROSS-1",
            "changes": [
                {
                    "component_id": component_b.id,
                    "title": "Cambio",
                    "description": "Descripción",
                }
            ],
        },
    )

    assert response.status_code == 404


def test_create_ticket_requires_at_least_one_change(client, project_factory):
    project = project_factory()

    response = client.post(
        f"/projects/{project.id}/tickets",
        json={
            "ticket_key": "EMPTY-1",
            "title": "Sin cambios",
            "description": "No debe aceptarse",
            "ticket_url": "https://example.com/EMPTY-1",
            "changes": [],
        },
    )

    assert response.status_code == 422


def test_list_tickets_includes_changes(client, project_factory, component_factory, ticket_factory):
    project = project_factory()
    component = component_factory(project.id)
    ticket_factory(project.id, components=[(component, 1)])

    response = client.get(f"/projects/{project.id}/tickets")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["changes"][0]["component_id"] == component.id


def test_update_ticket_and_reject_empty_update(client, project_factory, ticket_factory):
    project = project_factory()
    ticket = ticket_factory(project.id)

    updated = client.patch(
        f"/tickets/{ticket.id}",
        json={"title": "Título nuevo", "description": "Descripción nueva"},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Título nuevo"

    empty_update = client.patch(f"/tickets/{ticket.id}", json={})
    assert empty_update.status_code == 400


def test_update_ticket_rejects_duplicate_key(
    client, project_factory, ticket_factory
):
    project = project_factory()
    ticket_a = ticket_factory(project.id, ticket_key="KEY-A")
    ticket_factory(project.id, ticket_key="KEY-B")

    response = client.patch(
        f"/tickets/{ticket_a.id}",
        json={"ticket_key": "KEY-B"},
    )

    assert response.status_code == 409
