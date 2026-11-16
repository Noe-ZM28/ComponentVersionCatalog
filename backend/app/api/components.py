from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.component import Component
from app.models.project import Project
from app.schemas.component import ComponentCreate, ComponentResponse
from app.services.component_service import update_components_service

router = APIRouter()

@router.post("/projects/{project_id}/components", response_model=ComponentResponse, status_code=201)
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

@router.post("/projects/{project_id}/components/update", status_code=201)
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
