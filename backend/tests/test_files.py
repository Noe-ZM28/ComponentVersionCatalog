import json
import app.main as main_module
from sqlalchemy import select
from app.models.change_file import ChangeFile
from app.models.file_record import FileRecord

def test_upload_and_download_file(client, project_factory, component_factory, ticket_factory):
    project = project_factory()
    component = component_factory(project.id)
    ticket = ticket_factory(project.id, components=[(component, 1)])
    change = ticket.changes[0]
    metadata = [
        {
            "type_file": "source",
            "role": "attachment",
            "description": "Archivo de prueba",
        }
    ]

    upload = client.post(
        f"/projects/{project.id}/changes/{change.id}/files/uploadfiles",
        data={"metadata": json.dumps(metadata)},
        files=[("files", ("sample.txt", b"contenido de prueba", "text/plain"))],
    )

    assert upload.status_code == 200
    uploaded_file = upload.json()["files"][0]
    assert upload.json()["count_files_uploaded"] == 1
    assert uploaded_file["original_name"] == "sample.txt"
    assert uploaded_file["type_file"] == "source"

    download = client.get(
        f"/projects/{project.id}/changes/{change.id}/files/"
        f"{uploaded_file['file_id']}/download"
    )

    assert download.status_code == 200
    assert download.content == b"contenido de prueba"
    assert "sample.txt" in download.headers["content-disposition"]


def test_upload_rejects_invalid_json_metadata(client, project_factory, component_factory, ticket_factory):
    project = project_factory()
    component = component_factory(project.id)
    ticket = ticket_factory(project.id, components=[(component, 1)])

    response = client.post(
        f"/projects/{project.id}/changes/{ticket.changes[0].id}/files/uploadfiles",
        data={"metadata": "not-json"},
        files=[("files", ("sample.txt", b"x", "text/plain"))],
    )

    assert response.status_code == 400


def test_upload_rejects_metadata_file_count_mismatch(
    client, project_factory, component_factory, ticket_factory
):
    project = project_factory()
    component = component_factory(project.id)
    ticket = ticket_factory(project.id, components=[(component, 1)])

    response = client.post(
        f"/projects/{project.id}/changes/{ticket.changes[0].id}/files/uploadfiles",
        data={"metadata": json.dumps([])},
        files=[("files", ("sample.txt", b"x", "text/plain"))],
    )

    assert response.status_code == 400


def test_upload_rejects_file_for_unknown_change(client, project_factory):
    project = project_factory()

    response = client.post(
        f"/projects/{project.id}/changes/9999/files/uploadfiles",
        data={"metadata": json.dumps([])},
        files=[("files", ("sample.txt", b"x", "text/plain"))],
    )

    assert response.status_code == 404


def test_download_rejects_file_not_associated_with_change(
    client, project_factory, component_factory, ticket_factory
):
    project = project_factory()
    component = component_factory(project.id)
    ticket = ticket_factory(project.id, components=[(component, 1)])
    change = ticket.changes[0]

    response = client.get(
        f"/projects/{project.id}/changes/{change.id}/files/9999/download"
    )

    assert response.status_code == 404


async def failing_on_second_file(file, project_id):
    raise RuntimeError("Error simulado durante la subida")


def test_upload_failure_removes_previously_saved_files(
    client, project_factory, component_factory, ticket_factory,
    tmp_path, monkeypatch, session_factory
):
    project = project_factory()
    component = component_factory(project.id)
    ticket = ticket_factory(
        project.id,
        components=[(component, 1)],
    )
    change = ticket.changes[0]

    original_save = main_module.save_file_to_storage
    calls = 0

    async def save_then_fail(file, project_id):
        nonlocal calls
        calls += 1

        if calls == 1:
            return await original_save(file, project_id)

        return await failing_on_second_file(file, project_id)

    monkeypatch.setattr(
        main_module,
        "save_file_to_storage",
        save_then_fail,
    )

    metadata = [
        {
            "type_file": "source",
            "role": "before",
            "description": "Primer archivo",
        },
        {
            "type_file": "source",
            "role": "after",
            "description": "Segundo archivo",
        },
    ]

    response = client.post(
        f"/projects/{project.id}/changes/{change.id}/files/uploadfiles",
        data={"metadata": json.dumps(metadata)},
        files=[
            ("files", ("first.txt", b"primer contenido", "text/plain")),
            ("files", ("second.txt", b"segundo contenido", "text/plain")),
        ],
    )

    assert response.status_code == 500
    assert calls == 2

    # El primer archivo se había guardado físicamente.
    # Después del fallo, el directorio debe quedar sin archivos.
    project_storage = tmp_path / "files" / str(project.id)

    remaining_files = (
        list(project_storage.iterdir())
        if project_storage.exists()
        else []
    )

    assert remaining_files == []

    with session_factory() as session:
        assert session.scalar(select(FileRecord)) is None
        assert session.scalar(select(ChangeFile)) is None

def test_upload_multiple_files_creates_all_associations(
    client, project_factory, component_factory, ticket_factory
):
    project = project_factory()
    component = component_factory(project.id)
    ticket = ticket_factory(
        project.id,
        components=[(component, 1)],
    )
    change = ticket.changes[0]

    metadata = [
        {
            "type_file": "source",
            "role": "before",
            "description": "Código anterior",
        },
        {
            "type_file": "source",
            "role": "after",
            "description": "Código actualizado",
        },
    ]

    response = client.post(
        f"/projects/{project.id}/changes/{change.id}/files/uploadfiles",
        data={"metadata": json.dumps(metadata)},
        files=[
            ("files", ("before.txt", b"contenido anterior", "text/plain")),
            ("files", ("after.txt", b"contenido nuevo", "text/plain")),
        ],
    )

    assert response.status_code == 200

    result = response.json()

    assert result["count_files_uploaded"] == 2
    assert len(result["files"]) == 2

    assert {
        item["original_name"] for item in result["files"]
    } == {"before.txt", "after.txt"}

    assert {
        item["role"] for item in result["files"]
    } == {"before", "after"}

    assert all(item["file_id"] for item in result["files"])
