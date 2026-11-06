from datetime import datetime, timezone
import random
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Change, Component, Project, Ticket


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


def _create_generated_changes(db: Session) -> dict[str, int]:
    created = {"projects": 0, "components": 0, "tickets": 0, "changes": 0}
    projects = list(db.scalars(select(Project).order_by(Project.id)).all())
    components = list(db.scalars(select(Component).order_by(Component.id)).all())
    existing_project_names = {project.name for project in projects}
    change_count = random.randint(1, 15)

    for _ in range(change_count):
        if not projects:
            mode = "new_project"
        elif not components:
            mode = "new_component"
        else:
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
                    cust_num=random.randint(100, 999),
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
                ref_id=f"REF-{token}",
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
    generated = _create_generated_changes(db)
    for key in ("projects", "components", "tickets", "changes"):
        created[key] += generated[key]
    created["generated_changes"] = generated["generated_changes"]

    db.commit()
    return created
