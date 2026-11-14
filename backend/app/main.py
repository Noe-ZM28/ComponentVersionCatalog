from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload

from pydantic import ValidationError

from app.database import get_db

from app.models.change import Change
from app.models.change_file import ChangeFile
from app.models.component import Component
from app.models.file_record import FileRecord
from app.models.project import Project
from app.models.ticket import Ticket

from app.schemas.project import ProjectCreate, ProjectResponse, ProjectDetailResponse
from app.schemas.component import ComponentCreate, ComponentResponse
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate
from app.schemas.change import ChangeCreate, ChangeResponse, ChangeUpdate

from app.schemas.file_record import FileRecordResponse, FileUploadMetadata

from app.config import settings

from app.services.catalog_seed import seed_catalog
from app.services.component_service import update_components_service
from app.services.project_service import update_projects_service
from app.services.file_service import save_file_to_storage, get_file_path

from typing import Annotated

import json

import os
from pathlib import Path


app = FastAPI(
    title=settings.app_name,
    description="API para administrar proyectos, componentes e historial de cambios.",
    version="0.1.0",
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
app.mount(
    "/css",
    StaticFiles(directory=REPOSITORY_ROOT / "css"),
    name="frontend-css",
)
app.mount(
    "/js",
    StaticFiles(directory=REPOSITORY_ROOT / "js"),
    name="frontend-js",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "application": settings.app_name,
    }

@app.get("/about")
def about():
    return {
        "project": "Component Version Catalog",
        "version": "0.1.0",
        "database": "Microsoft SQL Server",
    }


@app.post("/catalog/seed-demo")
def seed_demo_catalog(db: Session = Depends(get_db)):
    created = seed_catalog(db)
    return {
        "message": "Catálogo de demostración cargado.",
        "created": created,
    }
    
@app.get("/")
def root():
    return FileResponse(REPOSITORY_ROOT / "index.html")

@app.get("/hello")
def hello():
    return{
        "message": "Hola Desarrollador",
        "application": settings.app_name,
    }

@app.get("/projects", response_model=list[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db)
    ):
    statement = select(Project).order_by(Project.id)
    projects = db.scalars(statement).all()

    return projects

@app.get("/projects/{project_id}", response_model=ProjectDetailResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db)
    ):
    statement = (
        select(Project)
        .where(Project.id == project_id)
        .options(
            selectinload(Project.components),
            selectinload(Project.tickets)
            .selectinload(Ticket.changes)
            .selectinload(Change.files)
            .selectinload(ChangeFile.file),
        )
    )
    project = db.scalars(statement).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="No existe un proyecto con ese ID."
        )

    return project

@app.post("/projects/update", status_code=201)
def update_projects(
    db: Session = Depends(get_db),
    ):
    state_projects = update_projects_service(db)
    return {
        "new_projects":     [f"{project.cust_num} · {project.name}" for project in state_projects["new_projects"]],
        "updated_projects": [f"{project.cust_num} · {project.name}" for project in state_projects["updated_projects"]],
        "skipped_projects": [f"{project.cust_num} · {project.name}" for project in state_projects["skipped_projects"]],
    }

@app.post("/projects", response_model=ProjectResponse, status_code=201)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db)
    ):
    existing_project = db.query(Project).filter(
        Project.name == project_data.name
    ).first()

    if existing_project:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un proyecto con ese nombre."
        )

    new_project = Project(
        name=project_data.name,
        description=project_data.description,
        cust_num=project_data.cust_num,
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project

@app.post("/projects/{project_id}/components", response_model=ComponentResponse, status_code=201)
def create_component(
    project_id: int,
    component_data: ComponentCreate,
    db: Session = Depends(get_db)
    ):

    project_statement = (
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.components))
    )
    project = db.scalars(project_statement).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="No existe un proyecto con ese nombre."
        )
    
    component_statement = select(Component).where(
        Component.project_id == project_id,
        Component.name == component_data.name,
    )
    component_exists = db.scalars(component_statement).first()

    if component_exists:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un componente con ese nombre en el proyecto."
        )

    new_component = Component(
        project_id=project_id,
        name=component_data.name,
        description=component_data.description,
        ref_id=component_data.ref_id,
        type_component=component_data.type_component,
        source_reference=component_data.source_reference,
    )

    project.components.append(new_component)
    db.commit()
    db.refresh(new_component)

    return new_component

@app.post("/projects/{project_id}/components/update", status_code=201)
def update_components(
    project_id: int,
    db: Session = Depends(get_db),
    ):

    state_components = update_components_service(project_id, db)
    return{
        "new_components":     [f"{component.ref_id}: {component.name}" for component in state_components["new_components"]],
        "updated_components": [f"{component.ref_id}: {component.name}" for component in state_components["updated_components"]],
        "skipped_components": [f"{component.ref_id}: {component.name}" for component in state_components["skipped_components"]],
    }


@app.post("/projects/{project_id}/tickets", response_model=TicketResponse, status_code=201)
def create_ticket(
    project_id:int,
    ticket_data: TicketCreate,
    db: Session = Depends(get_db)
    ):

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=404,
            detail="No existe un proyecto con ese nombre."
        )

    ticket_key = db.query(Ticket).filter(Ticket.ticket_key == ticket_data.ticket_key).first()
    if ticket_key:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un ticket con esa clave."
        )

    changes = []
    next_numbers = {}
    for change in ticket_data.changes:
        component = db.query(Component).filter(
            Component.project_id == project_id,
            Component.id == change.component_id
        ).first()
        if not component:
            raise HTTPException(
                status_code=404,
                detail=f"No existe un componente con el ID '{change.component_id}' en el proyecto {project.name}."
            )

        if component.id in next_numbers:
            change_number = next_numbers[component.id]
        else:
            max_change_number = db.query(func.max(Change.change_number)).filter(
                Change.component_id == component.id
            ).scalar()
            change_number = max_change_number + 1 if max_change_number is not None else 1

        next_numbers[component.id] = change_number + 1
        new_change = Change(
            project_id=project_id,
            component_id=component.id,
            change_number=change_number,
            title=change.title,
            description=change.description,
        )
        changes.append(new_change)

    new_ticket = Ticket(
        project_id=project_id,
        ticket_key=ticket_data.ticket_key,
        title=ticket_data.title,
        description=ticket_data.description,
        ticket_url=ticket_data.ticket_url,
        changes = changes
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    return new_ticket

@app.get("/projects/{project_id}/tickets", response_model=list[TicketResponse])
def list_tickets(
    project_id: int,
    db: Session = Depends(get_db)
    ):

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=404,
            detail="No existe un proyecto con ese nombre."
        )

    statement = (
        select(Ticket)
        .where(Ticket.project_id == project_id)
        .order_by(Ticket.id)
        .options(selectinload(Ticket.changes))
    )
    tickets = db.scalars(statement).all()

    return tickets

@app.patch("/tickets/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db)
    ):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="No existe un ticket con ese ID."
        )

    data = ticket_data.model_dump(exclude_unset=True)

    if not data:
        raise HTTPException(
            status_code=400,
            detail="Sin actualización."
        )
    
    changes_to_apply = {key: value for key, value in data.items() if getattr(ticket, key) != value}
    if not changes_to_apply:
        raise HTTPException(
            status_code=400,
            detail="Sin cambios para aplicar."
        )

    if ticket_data.ticket_key is not None:
        exist_ticket = db.query(Ticket).filter(Ticket.ticket_key == ticket_data.ticket_key).first()
        if exist_ticket and exist_ticket.id != ticket_id:
            raise HTTPException(
                status_code=409,
                detail="Ya existe un ticket con esa llave."
            )

    for key, value in changes_to_apply.items():
        setattr(ticket, key, value)

    db.commit()
    db.refresh(ticket)

    return ticket

@app.patch("/change/{change_id}", response_model=ChangeResponse)
def update_change(
    change_id: int,
    change_data: ChangeUpdate,
    db: Session = Depends(get_db)
    ):
    change = db.query(Change).filter(Change.id == change_id).first()
    if not change:
        raise HTTPException(
            status_code=404,
            detail="No existe un cambio con ese ID."
        )

    data = change_data.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(
            status_code=400,
            detail="Sin actualización."
        )

    changes_to_apply = {key: value for key, value in data.items() if getattr(change, key) != value}
    if not changes_to_apply:
        raise HTTPException(
            status_code=400,
            detail="Sin cambios para aplicar."
        )

    if "component_id" in changes_to_apply:
        exist_component = db.query(Component).filter(Component.id == change_data.component_id).first()
        if not exist_component:
            raise HTTPException(
                status_code=404,
                detail="No existe un componente con ese ID."
            )

        if exist_component.project_id != change.project_id:
            raise HTTPException(
                status_code=400,
                detail="El componente no pertenece al mismo proyecto que el cambio."
            )

        max_change_number = db.query(func.max(Change.change_number)).filter(Change.component_id == exist_component.id).scalar()
        change.change_number=max_change_number + 1 if max_change_number is not None else 1

    for key, value in changes_to_apply.items():
        setattr(change, key, value)

    db.commit()
    db.refresh(change)

    return change

@app.post("/tickets/{ticket_id}", response_model=TicketResponse)
def add_changes_to_ticket(
    ticket_id: int,
    new_changes: list[ChangeCreate],
    db: Session = Depends(get_db)
    ):
    if not new_changes:
        raise HTTPException(
            status_code=400,
            detail="Debe proporcionar al menos un cambio."
        )

    statement = (
        select(Ticket)
        .where(Ticket.id == ticket_id)
        .options(selectinload(Ticket.changes), selectinload(Ticket.project))
    )
    ticket = db.scalars(statement).first()
    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="No existe un ticket con ese ID."
        )

    next_numbers = {}
    changes_to_add = []
    for change_data in new_changes:
        component = db.query(Component).filter(
            Component.project_id == ticket.project_id,
            Component.id == change_data.component_id
        ).first()
        if not component:
            raise HTTPException(
                status_code=404,
                detail=f"No existe un componente con el ID '{change_data.component_id}' en el proyecto {ticket.project.name}."
            )

        if component.id in next_numbers:
            next_number = next_numbers[component.id]
        else:
            max_change_number = db.query(func.max(Change.change_number)).filter(
                Change.component_id == component.id
            ).scalar()

            next_number = max_change_number + 1 if max_change_number is not None else 1

        next_numbers[component.id] = next_number + 1

        new_change = Change(
            project_id=ticket.project_id,
            component_id=component.id,
            change_number=next_number,
            title=change_data.title,
            description=change_data.description,
        )
        changes_to_add.append(new_change)

    ticket.changes.extend(changes_to_add)
    db.commit()
    db.refresh(ticket)

    return ticket

@app.post("/projects/{project_id}/changes/{change_id}/files/uploadfiles")
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

@app.get("/projects/{project_id}/changes/{change_id}/files/{file_id}/download", response_class=FileResponse)
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
