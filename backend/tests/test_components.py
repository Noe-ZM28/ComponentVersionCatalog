def test_create_component_preserves_all_fields(client, project_factory):
    project = project_factory()
    payload = {
        "name": "Componente API",
        "description": "Integración del canal empresarial",
        "cadena": "API",
        "step": 25,
        "ref_id": "REF-API-001",
        "type_component": "API",
        "source_reference": "services/payment-api",
    }

    response = client.post(f"/projects/{project.id}/components", json=payload)

    assert response.status_code == 201
    assert response.json() | {"id": None, "project_id": None} == {
        **payload,
        "id": None,
        "project_id": None,
    }
    assert response.json()["project_id"] == project.id


def test_create_component_for_missing_project_returns_not_found(client):
    response = client.post(
        "/projects/9999/components",
        json={
            "name": "No existe",
            "description": "Componente",
            "cadena": "API",
            "step": 1,
        },
    )

    assert response.status_code == 404


def test_duplicate_component_name_returns_conflict(
    client, project_factory, component_factory
):
    project = project_factory()
    component_factory(project.id, name="Componente único")

    response = client.post(
        f"/projects/{project.id}/components",
        json={
            "name": "Componente único",
            "description": "Duplicado",
            "cadena": "API",
            "step": 2,
        },
    )

    assert response.status_code == 409


def test_component_step_must_be_positive(client, project_factory):
    project = project_factory()

    response = client.post(
        f"/projects/{project.id}/components",
        json={
            "name": "Paso inválido",
            "description": "Paso cero",
            "cadena": "API",
            "step": 0,
        },
    )

    assert response.status_code == 422


def test_component_type_must_be_an_enum_value(client, project_factory):
    project = project_factory()

    response = client.post(
        f"/projects/{project.id}/components",
        json={
            "name": "Tipo inválido",
            "description": "Componente",
            "cadena": "API",
            "step": 1,
            "type_component": "repository",
        },
    )

    assert response.status_code == 422


def test_update_components_passes_project_id_and_reports_not_implemented(
    client, project_factory, monkeypatch
):
    from app import main

    project = project_factory()
    calls = []
    monkeypatch.setattr(
        main, "update_components", lambda project_id: calls.append(project_id)
    )

    response = client.post(f"/projects/{project.id}/components/update")

    assert calls == [project.id]
    assert response.status_code == 501
    assert response.json()["detail"] == (
        "La actualización de componentes aún no está implementada."
    )


def test_update_components_for_missing_project_returns_not_found(client):
    response = client.post("/projects/9999/components/update")

    assert response.status_code == 404
