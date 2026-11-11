from ..database import external_engine
from sqlalchemy import text

from app.models.component import Component


def get_proyects_list() -> list[dict]:
    with external_engine.connect() as connection:
        result = connection.execute(
            text("""
                EXEC [CDSPLUS].[dbo].[GetListProjects]
            """),
        )

        projects = result.mappings().all()
        return [dict(project) for project in projects]

def get_component_list(cust_num: str) -> list[dict]:
    with external_engine.connect() as connection:
        result = connection.execute(
            text("""
                EXEC [CDSPLUS].[dbo].[GetListComponentsByProyect]
                :cust_num
            """),
            parameters={"cust_num": cust_num}
        )

        components = result.mappings().all()
        return [dict(component) for component in components]
