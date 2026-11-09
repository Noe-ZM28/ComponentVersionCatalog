from ..repositories.external_repository import get_proyects_list
from app.models.project import Project

from sqlalchemy import select
from sqlalchemy.orm import Session


def update_projects_service(db: Session) -> dict:
    type_projects = {
        "new_projects": [],
        "updated_projects": [],
        "skipped_projects": [],
    }

    list_projects = get_proyects_list()
    if not list_projects:
        return type_projects

    for project in list_projects:
        statement = select(Project).where(Project.cust_num == project["cust_num"])
        exist_project = db.scalars(statement).first()

        if exist_project:
            if (
                exist_project.name != project["name"]
                or exist_project.description != project["description"]
            ):
                exist_project.name = project["name"]
                exist_project.description = project["description"]
                type_projects["updated_projects"].append(exist_project)
            else:
                type_projects["skipped_projects"].append(exist_project)
        else:
            new_project = Project(
                name=project["name"],
                description=project["description"],
                cust_num=project["cust_num"],
            )
            type_projects["new_projects"].append(new_project)

    if type_projects["new_projects"]:
        db.add_all(type_projects["new_projects"])

    if type_projects["new_projects"] or type_projects["updated_projects"]:
        db.commit()

    return type_projects
