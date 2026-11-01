from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Project, Component
from app.schemas.project import ProjectCreate, ProjectResponse
from app.schemas.component import ComponentCreate, ComponentResponse

from app.config import settings


app = FastAPI(
    title=settings.app_name,
    description="API para administrar proyectos, componentes e historial de cambios.",
    version="0.1.0",
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
        "database": "SQLite",
    }
    
@app.get("/")
def root():
    return{
        "message": "Bienvenido a la API de Component Version Catalog",
    }

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

@app.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db)
    ):
    project = db.get(Project, project_id)

    if not project:
        raise HTTPException(
            status_code=404,
            detail="No existe un proyecto con ese ID."
        )

    return project

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
        description=project_data.description
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

    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="No existe un proyecto con ese nombre."
        )
    
    component_exists = db.query(Component).filter(
        Component.project_id == project_id,
        Component.name == component_data.name).first()

    if component_exists:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un componente con ese nombre en el proyecto."
        )

    new_component = Component(
        project_id=project_id,
        name=component_data.name,
        description=component_data.description,
        cadena=component_data.cadena,
        step=component_data.step
    )

    project.components.append(new_component)
    db.commit()
    db.refresh(new_component)

    return new_component

@app.get("/projects/{project_id}/components", response_model=list[ComponentResponse])
def list_components(
    project_id: int,
    db: Session = Depends(get_db)
    ):

    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="No existe un proyecto con ese nombre."
        )

    components = db.query(Component).filter(Component.project_id == project_id).all()

    return components



