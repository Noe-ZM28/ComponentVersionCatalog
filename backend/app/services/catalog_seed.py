from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
import random
from uuid import uuid4

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
        "REP", 1, "Operaciones", "Approved", "Reporte mensual de producción",
        "1.0", "DEMO-P1-RPT1", "2026-10-19",
        "Actualización de archivos y ejemplo del reporte PDF.", 3,
    ),
    CatalogRecord(
        "Proyecto 1", "Reporte RCP", "Reporte",
        "Archivos del reporte organizados en su carpeta, con una carpeta Example para la salida de muestra.",
        "REP", 2, "Operaciones", "Approved", "Reporte RCP",
        "1.0", "DEMO-P1-RPT2", "2026-10-19",
        "Actualización de archivos y ejemplo del reporte Archivo RCP.", 4,
    ),
    CatalogRecord(
        "Proyecto 2", "Reporte de producción", "Reporte",
        "Archivos del reporte organizados en su carpeta, con una carpeta Example para la salida de muestra.",
        "REP", 3, "Operaciones", "Approved", "Reporte de producción",
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

_BANK_PROJECTS = {
    "Mexico": (
        "Banco Horizonte del Bajio",
        "Banco Sierra de Plata",
        "Banco Valle Esmeralda",
        "Banco Costa del Sol Mexicano",
        "Banco Camino Real",
        "Banco Union del Pacifico",
    ),
    "Europa": (
        "Banco Aurora Iberico",
        "Northstar Union Bank",
        "Banco Riviera Centrale",
        "Danubia Credit House",
        "Banco Mercurio Europeo",
        "Baltic Crown Bank",
    ),
    "Africa": (
        "Ubuntu Continental Bank",
        "Banco Sahel Dorado",
        "Kilimanjaro Trade Bank",
        "Nile Crescent Finance",
        "Banco Costa de Marfil",
        "Savanna Trust Bank",
    ),
    "Medio Oriente": (
        "Cedar Gate Bank",
        "Banco Oasis del Levante",
        "Pearl Crescent Finance",
        "Atlas Gulf Banking",
        "Banco Duna Dorada",
        "Palm Horizon Bank",
    ),
}
_BANK_REGION_BY_NAME = {
    name: region
    for region, bank_names in _BANK_PROJECTS.items()
    for name in bank_names
}
_PROJECT_DESCRIPTIONS = (
    "Programa de modernizacion de pagos para operaciones en {region}.",
    "Iniciativa de integracion de canales y servicios financieros de {region}.",
    "Proyecto de estandarizacion de productos digitales para {region}.",
    "Plataforma de intercambio y conciliacion bancaria para {region}.",
)
_GENERATED_COMPONENT_TYPES = (
    ("PC1", "Configuracion de emision y personalizacion de tarjetas"),
    ("Reporte", "Generacion y distribucion de reportes operativos"),
    ("Carrier", "Integracion de paquetes y perfiles de personalizacion"),
    ("API", "Exposicion de servicios de consulta e integracion"),
    ("Batch", "Procesamiento y conciliacion de lotes"),
    ("Seguridad", "Validacion de controles y politicas de acceso"),
)
_CHAIN_METHODS = {
    "AUT": "Autorizacion de transacciones",
    "BIL": "Facturacion y liquidacion",
    "CAR": "Personalizacion de tarjetas",
    "CON": "Conciliacion de operaciones",
    "DAT": "Intercambio y validacion de datos",
    "EMI": "Emision de productos",
    "INT": "Integracion entre plataformas",
    "PAG": "Procesamiento de pagos",
    "REP": "Generacion de reportes",
    "SEG": "Validacion de seguridad",
}
_COMPONENT_DESCRIPTIONS = (
    "{purpose}; integrado con {system} y validado en ambiente {environment}.",
    "{purpose}; procesa {volume} operaciones por ciclo y conserva trazabilidad.",
    "{purpose}; intercambia datos mediante {system} con controles de consistencia.",
    "{purpose}; preparado para el canal {channel} y la region {region}.",
)
_TICKET_TITLES = (
    "Actualizacion de {area} para {component}",
    "Ajuste operativo de {component}",
    "Mejora de integracion: {component}",
    "Validacion de cambios en {component}",
    "Entrega de mantenimiento para {component}",
)
_TICKET_DESCRIPTIONS = (
    "Solicitud del equipo de {team} para revisar {area}. Se adjuntan criterios de validacion y alcance funcional.",
    "Trabajo coordinado con {team}; incluye pruebas de regresion y verificacion de datos de ejemplo.",
    "Cambio solicitado para mejorar {area}, con validacion en ambiente {environment}.",
    "Seguimiento de la iniciativa {initiative}; requiere confirmar resultados con el equipo de {team}.",
)
_CHANGE_TITLES = (
    "Ajuste de {area}",
    "Actualizacion de reglas de {area}",
    "Mejora de validacion para {area}",
    "Optimizacion del proceso de {area}",
    "Alineacion de datos de {area}",
)
_CHANGE_DESCRIPTIONS = (
    "Se actualiza {area} para {goal}; se verifican resultados con {system}.",
    "Se incorpora una validacion adicional de {field} y se documenta el resultado esperado.",
    "Se ajusta el flujo de {area} para reducir inconsistencias y facilitar su monitoreo.",
    "Se normaliza el intercambio de {field} entre {system} y el proceso de negocio.",
    "Se refuerza el control de {area} con pruebas de aceptacion y trazabilidad.",
)
_GENERATION_MODES = ("existing_component", "new_component", "new_project")


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


def _create_generated_changes(db: Session) -> dict[str, int]:
    created = {"projects": 0, "components": 0, "tickets": 0, "changes": 0}
    projects = list(db.scalars(select(Project).order_by(Project.id)).all())
    components = list(db.scalars(select(Component).order_by(Component.id)).all())
    existing_project_names = {project.name for project in projects}
    change_count = random.randint(1, 15)

    for _ in range(change_count):
        mode = random.choice(_GENERATION_MODES)
        token = uuid4().hex[:12].upper()

        if mode == "new_project":
            available_banks = [
                (region, name)
                for region, bank_names in _BANK_PROJECTS.items()
                for name in bank_names
                if name not in existing_project_names
            ]
            if available_banks:
                region, name = random.choice(available_banks)
                project = Project(
                    name=name,
                    description=random.choice(_PROJECT_DESCRIPTIONS).format(
                        region=region
                    ),
                )
                db.add(project)
                db.flush()
                projects.append(project)
                existing_project_names.add(name)
                created["projects"] += 1
            else:
                project = random.choice(projects)
            create_component = True
        elif mode == "new_component":
            project = random.choice(projects)
            create_component = True
        else:
            component = random.choice(components)
            project = next(
                project
                for project in projects
                if project.id == component.project_id
            )
            create_component = False

        if create_component:
            category, purpose = random.choice(_GENERATED_COMPONENT_TYPES)
            chain, method = random.choice(list(_CHAIN_METHODS.items()))
            step = random.randint(1, 25)
            system = random.choice(
                ("Switch Atlas", "Gateway Boreal", "Core Meridian", "Hub Nopal")
            )
            component_name = f"{category} - {chain} {token[:6]}"
            component = Component(
                project_id=project.id,
                name=component_name,
                description=random.choice(_COMPONENT_DESCRIPTIONS).format(
                    purpose=f"{purpose} ({method})",
                    system=system,
                    environment=random.choice(
                        ("integracion", "certificacion", "preproduccion")
                    ),
                    volume=random.choice(("2,500", "8,000", "12,000")),
                    channel=random.choice(
                        ("movil", "sucursal", "comercio", "empresarial")
                    ),
                    region=_BANK_REGION_BY_NAME.get(project.name)
                    or random.choice(tuple(_BANK_PROJECTS)),
                ),
                cadena=chain,
                step=step,
            )
            db.add(component)
            db.flush()
            components.append(component)
            created["components"] += 1

        change_number = (
            db.scalar(
                select(func.max(Change.change_number)).where(
                    Change.component_id == component.id
                )
            )
            or 0
        ) + 1
        area = random.choice(
            ("autorizaciones", "liquidaciones", "perfiles", "conciliaciones", "notificaciones")
        )
        field = random.choice(
            ("referencia", "fecha de proceso", "identificador de cuenta", "codigo de respuesta")
        )
        team = random.choice(
            ("operaciones", "integracion", "plataforma", "control de calidad")
        )
        environment = random.choice(
            ("integracion", "certificacion", "preproduccion")
        )
        initiative = random.choice(
            ("renovacion de canales", "estandarizacion regional", "modernizacion operativa")
        )
        component_context = {
            "area": area,
            "component": component.name,
            "team": team,
            "environment": environment,
            "initiative": initiative,
            "system": random.choice(
                ("Switch Atlas", "Gateway Boreal", "Core Meridian", "Hub Nopal")
            ),
            "field": field,
            "goal": random.choice(
                ("mejorar la consistencia", "reducir reprocesos", "facilitar el monitoreo")
            ),
        }
        title = random.choice(_TICKET_TITLES).format(**component_context)
        change_title = random.choice(_CHANGE_TITLES).format(**component_context)
        change_description = random.choice(_CHANGE_DESCRIPTIONS).format(
            **component_context
        )
        ticket_key = f"DEMO-{token}"
        ticket = Ticket(
            project_id=project.id,
            ticket_key=ticket_key,
            title=title,
            description=random.choice(_TICKET_DESCRIPTIONS).format(
                **component_context
            ),
            ticket_url=f"https://example.com/jira/{ticket_key}",
            changes=[
                Change(
                    project_id=project.id,
                    component_id=component.id,
                    change_number=change_number,
                    title=change_title,
                    description=change_description,
                    cadena=component.cadena,
                    step=component.step,
                    created_at=datetime.now(timezone.utc),
                )
            ],
        )
        db.add(ticket)
        db.flush()
        created["tickets"] += 1
        created["changes"] += 1

    created["generated_changes"] = change_count
    return created


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
        elif component.cadena in {"R01", "R02", "R03"}:
            component.cadena = record.chain

        for version, ticket_key, recorded_date, change_description in _version_history(record):
            ticket = db.scalar(
                select(Ticket).where(Ticket.ticket_key == ticket_key)
            )
            if ticket is not None and ticket.project_id != project.id:
                raise ValueError(
                    f"La clave de ticket '{ticket_key}' ya pertenece a otro proyecto."
                )

            if ticket is not None:
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
                    changes=[
                        Change(
                            project_id=project.id,
                            component_id=component.id,
                            change_number=last_number + 1,
                            title=f"Versión {version} - {status}",
                            description=change_description,
                            cadena=component.cadena,
                            step=component.step,
                            created_at=datetime.combine(
                                date.fromisoformat(recorded_date),
                                time.min,
                                tzinfo=timezone.utc,
                            ),
                        )
                    ],
                )
                db.add(ticket)
                created["tickets"] += 1
                created["changes"] += 1
                db.flush()
                continue

            db.add(
                Change(
                    project_id=project.id,
                    component_id=component.id,
                    ticket_id=ticket.id,
                    change_number=last_number + 1,
                    title=f"Versión {version} - {status}",
                    description=change_description,
                    cadena=component.cadena,
                    step=component.step,
                    created_at=datetime.combine(
                        date.fromisoformat(recorded_date),
                        time.min,
                        tzinfo=timezone.utc,
                    ),
                )
            )
            created["changes"] += 1

    generated = _create_generated_changes(db)
    for key in ("projects", "components", "tickets", "changes"):
        created[key] += generated[key]
    created["generated_changes"] = generated["generated_changes"]

    db.commit()
    return created
