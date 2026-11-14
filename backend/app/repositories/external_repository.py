from ..database import external_engine
from sqlalchemy import text

from app.models.component import Component

def exec_store_procedure(
    store_procedure: str,
    parameters: dict | None = None
    ) -> list[dict]:

    with external_engine.connect() as connection:

        query = f"EXEC {store_procedure}"

        if parameters:
            query += " " + ", ".join(
                f"@{key} = :{key}" for key in parameters
            )

        result = connection.execute(
            text(query),
            parameters or {}
        )

        records = result.mappings().all()

        return [dict(record) for record in records]


def get_proyects_list() -> list[dict]:
    return exec_store_procedure(
        "[CDSPLUS].[dbo].[GetListProjects]"
    )

def get_component_list(cust_num: str) -> list[list[dict[str, str]]]:
    carriers = get_carrier_list(cust_num)
    pc1 = get_pc1_list(cust_num)

    return [carriers, pc1]

def get_carrier_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        "[CDSPLUS].[dbo].[GetListCarrier]",
        {"cust_num": cust_num}
    )


def get_pc1_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        "[CDSPLUS].[dbo].[GetListPC1]",
        {"cust_num": cust_num}
    )

