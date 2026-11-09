from ..database import external_engine
from sqlalchemy import text

def get_proyects_list() -> list[dict]:
    with external_engine.connect() as connection:
        result = connection.execute(
            text("""
                EXEC [CDSPLUS].[dbo].[GetListProjects]
            """),
        )

        projects = result.mappings().all()
        return [dict(project) for project in projects]
