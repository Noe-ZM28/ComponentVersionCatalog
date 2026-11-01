from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Change, Component, Project, Ticket


@dataclass(frozen=True)
class CatalogRecord:
    project: str
    name: str
    category: str
    description: str
    chain: str
    step: int
    owner: str
    status: str
    scope: str
    current_version: str
    ticket_key: str
    recorded_date: str
    change: str
    history_index: int
    proposed_change: str | None = None
    current_change: str | None = None


_CATALOG = (
    CatalogRecord(
        "Proyecto 1", "PC1 - Banco 1", "PC1",
        "Ejemplo PC1 de texto plano con campos delimitados por etiquetas, siguiendo la estructura de los registros dummy.",
        "PRD", 12, "Equipo de configuración", "Approved", "PC1 - Banco 1",
        "1.0", "DEMO-101", "2026-10-01",
        "Actualización de estructura del registro PC1.", 0,
        proposed_change="Se propone actualizar el nombre de ejemplo del titular.",
        current_change="Se actualizó el dato de ciudad manteniendo la estructura de campos PC1.",
    ),
    CatalogRecord(
        "Proyecto 1", "PC1 - Banco 2", "PC1",
        "Ejemplo PC1 de texto plano con campos delimitados por etiquetas, siguiendo la estructura de los registros dummy.",
        "PRD", 12, "Equipo de configuración", "Approved", "PC1 - Banco 2",
        "1.1", "DEMO-102", "2026-10-02",
        "Actualización de estructura del registro PC1.", 1,
    ),
    CatalogRecord(
        "Proyecto 2", "PC1 - Banco 3", "PC1",
        "Ejemplo PC1 de texto plano con campos delimitados por etiquetas, siguiendo la estructura de los registros dummy.",
        "PRD", 12, "Equipo de configuración", "Approved", "PC1 - Banco 3",
        "1.0", "DEMO-201", "2026-10-08",
        "Actualización de estructura del registro PC1.", 2,
    ),
    CatalogRecord(
        "Proyecto 1", "Reporte mensual de producción", "Reporte",
        "Archivos del reporte organizados en su carpeta, con una carpeta Example para la salida de muestra.",
        "R01", 1, "Operaciones", "Approved", "Reporte mensual de producción",
        "1.0", "DEMO-P1-RPT1", "2026-10-19",
        "Actualización de archivos y ejemplo del reporte PDF.", 3,
    ),
    CatalogRecord(
        "Proyecto 1", "Reporte RCP", "Reporte",
        "Archivos del reporte organizados en su carpeta, con una carpeta Example para la salida de muestra.",
        "R02", 2, "Operaciones", "Approved", "Reporte RCP",
        "1.0", "DEMO-P1-RPT2", "2026-10-19",
        "Actualización de archivos y ejemplo del reporte Archivo RCP.", 4,
    ),
    CatalogRecord(
        "Proyecto 2", "Reporte de producción", "Reporte",
        "Archivos del reporte organizados en su carpeta, con una carpeta Example para la salida de muestra.",
        "R03", 3, "Operaciones", "Approved", "Reporte de producción",
        "1.0", "DEMO-P2-RPT1", "2026-10-19",
        "Actualización de archivos y ejemplo del reporte Archivo de texto.", 5,
        proposed_change="Se propone mostrar VALIDATED para los registros aprobados.",
        current_change="Se normalizaron los estados ACCEPTED y DECLINED a APPROVED y REJECTED.",
    ),
    CatalogRecord(
        "Proyecto 1", "Paquete 1", "Carrier",
        "Cada paquete incluye el archivo PKG3 en RichPDFPackage y los PDF de muestra de sus variantes en Example.",
        "CPP", 10, "Integración", "Approved", "Design 1",
        "1.0", "DEMO-CAR-P1-P1", "2026-10-14",
        "Actualización de variantes del paquete 1.", 6,
    ),
    CatalogRecord(
        "Proyecto 2", "Paquete 1", "Carrier",
        "Cada paquete incluye el archivo PKG3 en RichPDFPackage y los PDF de muestra de sus variantes en Example.",
        "CPP", 10, "Integración", "Approved", "Design 4",
        "1.0", "DEMO-CAR-P2-P1", "2026-10-15",
        "Actualización de variantes del paquete 1.", 7,
    ),
    CatalogRecord(
        "Proyecto 2", "Paquete 2", "Carrier",
        "Cada paquete incluye el archivo PKG3 en RichPDFPackage y los PDF de muestra de sus variantes en Example.",
        "CPP", 10, "Integración", "Approved", "Design 2",
        "1.0", "DEMO-CAR-P2-P2", "2026-10-16",
        "Actualización de variantes del paquete 2.", 8,
    ),
    CatalogRecord(
        "Proyecto 2", "Paquete 3", "Carrier",
        "Cada paquete incluye el archivo PKG3 en RichPDFPackage y los PDF de muestra de sus variantes en Example.",
        "CPP", 10, "Integración", "Approved", "Design 3",
        "1.0", "DEMO-CAR-P2-P3", "2026-10-17",
        "Actualización de variantes del paquete 3.", 9,
    ),
)

_OLDER_CHANGES = (
    "Se normalizaron nombres y valores de campos para el ejemplo.",
    "Se incorporaron campos adicionales al registro de demostración.",
    "Se creó la primera versión del ejemplo estructurado.",
    "Se ajustó el formato del archivo de muestra.",
    "Se actualizaron campos opcionales del registro.",
    "Se revisó la estructura para mantener compatibilidad.",
)


def _version_history(record: CatalogRecord) -> list[tuple[str, str, str, str]]:
    major, minor = (int(part) for part in record.current_version.split("."))
    previous_version = (
        f"{major}.{minor - 1}"
        if minor > 0
        else f"{max(0, major - 1)}.9"
    )
    current_date = date.fromisoformat(record.recorded_date)
    previous_date = current_date - timedelta(days=30)
    proposed_change = record.proposed_change or record.change
    current_change = record.current_change or record.change

    history = [
        (
            f"{major}.{minor + 1}",
            f"{record.ticket_key}-REV",
            "2026-10-19",
            f"Propuesta: {proposed_change}",
        ),
        (
            record.current_version,
            record.ticket_key,
            current_date.isoformat(),
            current_change,
        ),
        (
            previous_version,
            f"{record.ticket_key}-PREV",
            previous_date.isoformat(),
            "Versión anterior conservada para consulta histórica.",
        ),
    ]

    older_count = 1 + record.history_index
    for index in range(older_count):
        older_date = previous_date - timedelta(days=30 * (index + 1))
        history.append(
            (
                f"0.{9 - index:02d}",
                f"{record.ticket_key}-HIST-{index + 1}",
                older_date.isoformat(),
                _OLDER_CHANGES[index % len(_OLDER_CHANGES)],
            )
        )

    return sorted(history, key=lambda version: version[2])


def seed_catalog(db: Session) -> dict[str, int]:
    created = {"projects": 0, "components": 0, "tickets": 0, "changes": 0}

    for record in _CATALOG:
        project = db.scalar(select(Project).where(Project.name == record.project))
        if project is None:
            project = Project(
                name=record.project,
                description="Proyecto de demostración importado desde js/data.js.",
            )
            db.add(project)
            db.flush()
            created["projects"] += 1

        component = db.scalar(
            select(Component).where(
                Component.project_id == project.id,
                Component.name == record.name,
            )
        )
        if component is None:
            component = Component(
                project_id=project.id,
                name=record.name,
                description=(
                    f"[{record.category}] {record.description}\n"
                    f"Estado: {record.status}. Responsable: {record.owner}. "
                    f"Alcance: {record.scope}."
                ),
                cadena=record.chain,
                step=record.step,
            )
            db.add(component)
            db.flush()
            created["components"] += 1

        for version, ticket_key, recorded_date, change_description in _version_history(record):
            ticket = db.scalar(
                select(Ticket).where(Ticket.ticket_key == ticket_key)
            )
            if ticket is None:
                ticket = Ticket(
                    ticket_key=ticket_key,
                    project_id=project.id,
                    title=change_description,
                    description=(
                        f"Cambio de demostración para {record.name}, "
                        f"versión {version}."
                    ),
                    ticket_url=f"https://example.com/jira/{ticket_key}",
                    registered_at=datetime.combine(
                        date.fromisoformat(recorded_date),
                        time.min,
                        tzinfo=timezone.utc,
                    ),
                )
                db.add(ticket)
                db.flush()
                created["tickets"] += 1

            existing_change = db.scalar(
                select(Change).where(
                    Change.component_id == component.id,
                    Change.ticket_id == ticket.id,
                )
            )
            if existing_change is not None:
                continue

            last_number = db.scalar(
                select(func.max(Change.change_number)).where(
                    Change.component_id == component.id
                )
            ) or 0
            if ticket_key.endswith("-REV"):
                status = "In Review"
            elif ticket_key == record.ticket_key:
                status = "Approved"
            else:
                status = "Deprecated"
            db.add(
                Change(
                    project_id=project.id,
                    component_id=component.id,
                    ticket_id=ticket.id,
                    change_number=last_number + 1,
                    title=f"Versión {version} - {status}",
                    description=change_description,
                    cadena=record.chain,
                    step=record.step,
                    created_at=datetime.combine(
                        date.fromisoformat(recorded_date),
                        time.min,
                        tzinfo=timezone.utc,
                    ),
                )
            )
            created["changes"] += 1

    db.commit()
    return created
