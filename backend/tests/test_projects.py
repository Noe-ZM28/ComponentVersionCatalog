def test_health_and_root_endpoints(client):
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/").status_code == 200
    assert client.get("/about").json()["database"] == "SQLite"
    assert client.get("/hello").status_code == 200


def test_create_and_list_projects(client):
    response = client.post(
        "/projects",
        json={
            "name": "Banco Demo",
            "description": "Proyecto regional",
            "cust_num": 4872,
        },
    )

    assert response.status_code == 201
    project = response.json()
    assert project["name"] == "Banco Demo"
    assert project["cust_num"] == 4872
    assert project["components"] == []

    listed = client.get("/projects")
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [project["id"]]
    assert listed.json()[0]["cust_num"] == 4872


def test_create_project_allows_missing_cust_num(client):
    response = client.post(
        "/projects",
        json={"name": "Banco sin CustNum", "description": "Proyecto regional"},
    )

    assert response.status_code == 201
    assert response.json()["cust_num"] is None


def test_create_project_rejects_non_integer_cust_num(client):
    response = client.post(
        "/projects",
        json={
            "name": "Banco CustNum inválido",
            "description": "Proyecto regional",
            "cust_num": "no es entero",
        },
    )

    assert response.status_code == 422


def test_get_project_includes_components(client, project_factory, component_factory):
    project = project_factory()
    component_factory(
        project.id,
        name="Componente incluido",
        source_type="database",
        source_reference="catalog/components/demo",
    )

    response = client.get(f"/projects/{project.id}")

    assert response.status_code == 200
    assert response.json()["components"][0]["source_type"] == "database"
    assert response.json()["components"][0]["source_reference"] == "catalog/components/demo"


def test_create_duplicate_project_returns_conflict(client, project_factory):
    project_factory(name="Banco Duplicado")

    response = client.post(
        "/projects",
        json={"name": "Banco Duplicado", "description": "Otra descripción"},
    )

    assert response.status_code == 409


def test_get_missing_project_returns_not_found(client):
    assert client.get("/projects/9999").status_code == 404
