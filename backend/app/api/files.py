from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.change import Change
from app.models.change_file import ChangeFile
from app.models.file_record import FileRecord
from app.models.project import Project
from app.schemas.file_record import FileUploadMetadata
from app.services.file_service import save_file_to_storage, get_file_path
import json
import os

router = APIRouter()

@router.post("/projects/{project_id}/changes/{change_id}/files/uploadfiles")
async def upload_files(
    project_id: int,
    change_id: int,
    files: list[UploadFile] = File(...),
    metadata: str = Form(...),
    db: Session = Depends(get_db)):
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=404,
            detail="No existe un proyecto con ese nombre."
        )

    change = db.query(Change).filter(Change.id == change_id, Change.project_id == project_id).first()
    if not change:
        raise HTTPException(
            status_code=404,
            detail="No existe un cambio con ese ID en el proyecto."
        )

    try:
        metadata_data = json.loads(metadata)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="El campo 'metadata' no es un JSON válido."
        )

    if not isinstance(metadata_data, list):
        raise HTTPException(
            status_code=400,
            detail="El campo 'metadata' debe ser una lista de objetos."
        )

    try:
        valid_metadata = [FileUploadMetadata.model_validate(data) for data in metadata_data]
    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Los metadatos no son válidos: {e}"
        )

    if len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail="Debe subir al menos un archivo."
        )

    if len(valid_metadata) != len(files):
        raise HTTPException(
            status_code=400,
            detail="La cantidad de metadatos no coincide con la cantidad de archivos subidos."
        )

    path_files = []
    uploaded_files = []
    try:
        for file, metadata_item in zip(files, valid_metadata):
            stored_data = await save_file_to_storage(file, project_id)
            path_files.append(stored_data["storage_path"])

            file_record = FileRecord(
                type_file=metadata_item.type_file,
                original_name=stored_data["original_name"],
                stored_name=stored_data["stored_name"],
                storage_path=stored_data["storage_path"],
                content_type=stored_data["content_type"],
                size_bytes=stored_data["size_bytes"],
                sha256=stored_data["sha256"],
                )
            db.add(file_record)
            db.flush()  # Flush to get the file_record.id before committing

            change_file = ChangeFile(
                change_id=change.id,
                file_id = file_record.id,
                role=metadata_item.role,
                description=metadata_item.description,
                change=change,
                file=file_record
            )
            db.add(change_file)
            uploaded_files.append(change_file)

        db.commit()

    except Exception as e:
        # Rollback in case of any error during file processing
        db.rollback()
        for file in path_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except Exception as cleanup_error:
                print(f"Error al limpiar el archivo {file}: {cleanup_error}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar los archivos"
        )

    db.refresh(change)

    return {
        "change_id": change.id,
        "count_files_uploaded": len(uploaded_files),
        "files": [
            {
                "file_id": cf.file.id,
                "original_name": cf.file.original_name,
                "stored_name": cf.file.stored_name,
                "type_file": cf.file.type_file,
                "role": cf.role,
                "description": cf.description
            }
            for cf in uploaded_files
        ]
    }

@router.get("/projects/{project_id}/changes/{change_id}/files/{file_id}/download", response_class=FileResponse)
def download(
    project_id: int,
    change_id: int,
    file_id: int,
    db: Session = Depends(get_db)
    ):
    # Comprobar que existe el proyecto
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="No existe un proyecto con ese ID."
        )

    # Comprobar que el cambio pertenece al proyecto
    change = db.query(Change).filter(
        Change.id == change_id,
        Change.project_id == project_id
    ).first()

    if not change:
        raise HTTPException(
            status_code=404,
            detail="No existe un cambio con ese ID en el proyecto."
        )

    # Comprobar que el archivo está asociado al cambio
    file = (
        db.query(FileRecord)
        .join(ChangeFile, FileRecord.id == ChangeFile.file_id)
        .filter(
            ChangeFile.change_id == change_id,
            FileRecord.id == file_id
        )
        .first()
    )

    if not file:
        raise HTTPException(
            status_code=404,
            detail="El archivo no está asociado a este cambio."
        )

    # Obtener la ruta física
    file_path = get_file_path(project_id, file.stored_name)

    # Entregar el archivo al cliente
    return FileResponse(
        path=file_path,
        media_type=file.content_type,
        filename=file.original_name
    )
