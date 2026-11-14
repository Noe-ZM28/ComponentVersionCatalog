from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.repositories.external_repository import get_component_list

from app.models.component import Component
from app.models.project import Project


def update_components_service(project_id: int, db: Session) -> dict:
    type_components = {
        "new_components": [],
        "updated_components": [],
        "skipped_components": [],
    }

    project_statement = (
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.components))
    )

    project = db.scalars(project_statement).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="No existe un proyecto con ese ID."
        )

    if project.cust_num is None:
        raise HTTPException(
            status_code=400,
            detail="El proyecto no tiene un CustNum asociado."
        )

    list_components = get_component_list(str(project.cust_num))

    if not list_components:
        return type_components

    try:
        for component in list_components:

            generator = (d for d in project.components if d.ref_id == component["ref_id"])
            current_project_component = next(generator, None)

            if current_project_component:
                if (current_project_component.name != component["name"]
                    or current_project_component.description != component["description"]
                    or current_project_component.type_component != component["type_component"]):
                    current_project_component.name = component["name"]
                    current_project_component.description = component["description"]
                    current_project_component.type_component = component["type_component"]

                    type_components["updated_components"].append(current_project_component)

                else:
                    type_components["skipped_components"].append(current_project_component)

            else:
                new_component = Component(
                    project_id=project_id,
                    name=component["name"],
                    description=component["description"],
                    ref_id=component["ref_id"],
                    type_component=component["type_component"],
                    source_reference=None,
                    last_modified_at=component["last_modified_at"],
                )

                project.components.append(new_component)

                type_components["new_components"].append(new_component)

        if (type_components["new_components"] or type_components["updated_components"]):
            db.commit()

    except Exception:
        db.rollback()
        raise

    return type_components
