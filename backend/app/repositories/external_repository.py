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
    variables = get_variables_list(cust_num)
    dialogues = get_dialogues_list(cust_num)
    scripts = get_scripts_list(cust_num)
    recurringJobs = get_recurringJobs_list(cust_num)

    return [variables, dialogues, scripts, recurringJobs]

def get_variables_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        "[CDSPLUS].[dbo].[SP_GetVariables]",
        {"CustNum": cust_num}
    )

def get_dialogues_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        "[CDSPLUS].[dbo].[SP_GetDialogues]",
        {"CustNum": cust_num}
    )

def get_scripts_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        "[CDSPLUS].[dbo].[SP_GetScripts]",
        {"CustNum": cust_num}
    )

def get_recurringJobs_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        "[CDSPLUS].[dbo].[SP_GetRecurringJobs]",
        {"CustNum": cust_num}
    )

