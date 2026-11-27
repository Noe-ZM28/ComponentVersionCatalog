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
    dialogues = get_dialogues_list(cust_num)
    scripts = get_scripts_list(cust_num)
    variables = get_variables_list(cust_num)
    recurringJobs = get_recurringJobs_list(cust_num)
    chains = get_chains_list(cust_num)
    mappings = get_mappings_list(cust_num)
    file_definitions = get_file_definitions_list(cust_num)
    xml_templates = get_xml_templates_list(cust_num)
    sorting = get_sorting_list(cust_num)
    splits = get_splits_list(cust_num)
    dictionaries = get_dictionaries_list(cust_num)

    return [
        variables, dialogues, scripts,
        recurringJobs, chains, mappings,
        file_definitions, xml_templates,
        sorting, splits, dictionaries
    ]

def get_dialogues_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        "[CDSPLUSP].[dbo].[SP_GetDialogues]",
        {"CustNum": cust_num}
    )

def get_scripts_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        "[CDSPLUSP].[dbo].[SP_GetScripts]",
        {"CustNum": cust_num}
    )

def get_variables_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        "[CDSPLUSP].[dbo].[SP_GetVariables]",
        {"CustNum": cust_num}
    )

def get_recurringJobs_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        "[CDSPLUSP].[dbo].[SP_GetRecurringJobs]",
        {"CustNum": cust_num}
    )

def get_chains_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        "[CDSPLUSP].[dbo].[SP_GetChains]",
        {"CustNum": cust_num}
    )

def get_mappings_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        "[CDSPLUSP].[dbo].[SP_GetMappings]",
        {"CustNum": cust_num}
    )

def get_file_definitions_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        "[CDSPLUSP].[dbo].[SP_GetFileDefinitions]",
        {"CustNum": cust_num}
    )

def get_xml_templates_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        "[CDSPLUSP].[dbo].[SP_GetXMLTemplates]",
        {"CustNum": cust_num}
    )

def get_sorting_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        "[CDSPLUSP].[dbo].[SP_GetSorting]",
        {"CustNum": cust_num}
    )

def get_splits_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        "[CDSPLUSP].[dbo].[SP_GetSplit]",
        {"CustNum": cust_num}
    )

def get_dictionaries_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        "[CDSPLUSP].[dbo].[SP_GetDictionaries]",
        {"CustNum": cust_num}
    )


