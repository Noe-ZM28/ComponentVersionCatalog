from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.change import Change
from app.models.change_file import ChangeFile
from app.models.project import Project
from app.models.ticket import Ticket
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectDetailResponse
from app.services.project_service import update_projects_service

router = APIRouter()

@router.get("/projects", response_model=list[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db)
    ):
    statement = select(Project).order_by(Project.id)
    projects = db.scalars(statement).all()

    return projects

@router.get("/projects/{project_id}", response_model=ProjectDetailResponse)
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

@router.post("/projects/update", status_code=201)
def update_projects(
    db: Session = Depends(get_db),
    ):
    state_projects = update_projects_service(db)
    return {
        "new_projects":     [f"{project.cust_num} · {project.name}" for project in state_projects["new_projects"]],
        "updated_projects": [f"{project.cust_num} · {project.name}" for project in state_projects["updated_projects"]],
        "skipped_projects": [f"{project.cust_num} · {project.name}" for project in state_projects["skipped_projects"]],
    }

@router.post("/projects", response_model=ProjectResponse, status_code=201)
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
