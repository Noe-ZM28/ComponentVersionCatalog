import re
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import text

from ..config import settings
from ..database import external_engine


_PARAMETER_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _component_store_procedure(name: str) -> str:
    suffix = "Dummy" if settings.use_dummy_stored_procedures else ""
    return f"[CDSPLUSP].[dbo].[SP_Get{name}{suffix}]"


def exec_store_procedure(
    store_procedure: str,
    parameters: dict | None = None
    ) -> list[dict]:

    if external_engine is None:
        raise RuntimeError(
            "La conexión externa no está configurada. "
            "Verifica EXTERNAL_DATABASE_URL en el archivo .env."
        )

    if parameters:
        invalid_keys = [
            key for key in parameters
            if not isinstance(key, str) or not _PARAMETER_NAME.fullmatch(key)
        ]
        if invalid_keys:
            raise ValueError("Los nombres de los parámetros no son válidos.")

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

        records = []
        for partition in result.mappings().partitions(1000):
            records.extend(dict(record) for record in partition)

        return records


def get_proyects_list() -> list[dict]:
    return exec_store_procedure(
        "[CDSPLUS].[dbo].[GetListProjects]"
    )

def get_component_list(cust_num: str) -> list[list[dict[str, str]]]:
    loaders = (
        get_variables_list,
        get_dialogues_list,
        get_scripts_list,
        get_recurringJobs_list,
        get_chains_list,
        get_mappings_list,
        get_file_definitions_list,
        get_xml_templates_list,
        get_sorting_list,
        get_splits_list,
        get_dictionaries_list,
    )

    with ThreadPoolExecutor(max_workers=min(4, len(loaders))) as executor:
        futures = [executor.submit(loader, cust_num) for loader in loaders]
        return [future.result() for future in futures]

def get_dialogues_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        _component_store_procedure("Dialogues"),
        {"CustNum": cust_num}
    )

def get_scripts_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        _component_store_procedure("Scripts"),
        {"CustNum": cust_num}
    )

def get_variables_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        _component_store_procedure("Variables"),
        {"CustNum": cust_num}
    )

def get_recurringJobs_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        _component_store_procedure("RecurringJobs"),
        {"CustNum": cust_num}
    )

def get_chains_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        _component_store_procedure("Chains"),
        {"CustNum": cust_num}
    )

def get_mappings_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        _component_store_procedure("Mappings"),
        {"CustNum": cust_num}
    )

def get_file_definitions_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        _component_store_procedure("FileDefinitions"),
        {"CustNum": cust_num}
    )

def get_xml_templates_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        _component_store_procedure("XMLTemplates"),
        {"CustNum": cust_num}
    )

def get_sorting_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        _component_store_procedure("Sorting"),
        {"CustNum": cust_num}
    )

def get_splits_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        _component_store_procedure("Split"),
        {"CustNum": cust_num}
    )

def get_dictionaries_list(cust_num: str) -> list[dict[str, str]]:
    return exec_store_procedure(
        _component_store_procedure("Dictionaries"),
        {"CustNum": cust_num}
    )


