from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Project, Component, Ticket, Change
from app.schemas.project import ProjectCreate, ProjectResponse
from app.schemas.component import ComponentCreate, ComponentResponse
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate
from app.schemas.change import ChangeCreate, ChangeResponse, ChangeUpdate

from app.config import settings
from app.services.catalog_seed import seed_catalog


app = FastAPI(
    title=settings.app_name,
    description="API para administrar proyectos, componentes e historial de cambios.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "application": settings.app_name,
    }

@app.get("/about")
def about():
    return {
        "project": "Component Version Catalog",
        "version": "0.1.0",
        "database": "SQLite",
    }


@app.post("/catalog/seed-demo")
def seed_demo_catalog(db: Session = Depends(get_db)):
    created = seed_catalog(db)
    return {
        "message": "Catálogo de demostración cargado.",
        "created": created,
    }
    
@app.get("/")
def root():
    return{
        "message": "Bienvenido a la API de Component Version Catalog",
    }

@app.get("/hello")
def hello():
    return{
        "message": "Hola Desarrollador",
        "application": settings.app_name,
    }

@app.get("/projects", response_model=list[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db)
    ):
    statement = select(Project).order_by(Project.id).options(selectinload(Project.components))
    projects = db.scalars(statement).all()

    return projects

@app.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db)
    ):
    statement = select(Project).where(Project.id == project_id).options(selectinload(Project.components))
    project = db.scalars(statement).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="No existe un proyecto con ese ID."
        )

    return project

@app.post("/projects", response_model=ProjectResponse, status_code=201)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db)
    ):
    existing_project = db.query(Project).filter(
        Project.name == project_data.name
    ).first()

    if existing_project:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un proyecto con ese nombre."
        )

    new_project = Project(
        name=project_data.name,
        description=project_data.description
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project

@app.post("/projects/{project_id}/components", response_model=ComponentResponse, status_code=201)
def create_component(
    project_id: int,
    component_data: ComponentCreate,
    db: Session = Depends(get_db)
    ):

    project_statement = (
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.components))
    )
    project = db.scalars(project_statement).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="No existe un proyecto con ese nombre."
        )
    
    component_statement = select(Component).where(
        Component.project_id == project_id,
        Component.name == component_data.name,
    )
    component_exists = db.scalars(component_statement).first()

    if component_exists:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un componente con ese nombre en el proyecto."
        )

    new_component = Component(
        project_id=project_id,
        name=component_data.name,
        description=component_data.description,
        cadena=component_data.cadena,
        step=component_data.step
    )

    project.components.append(new_component)
    db.commit()
    db.refresh(new_component)

    return new_component

@app.post("/projects/{project_id}/tickets", response_model=TicketResponse, status_code=201)
def create_ticket(
    project_id:int,
    ticket_data: TicketCreate,
    db: Session = Depends(get_db)
    ):

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=404,
            detail="No existe un proyecto con ese nombre."
        )

    ticket_key = db.query(Ticket).filter(Ticket.ticket_key == ticket_data.ticket_key).first()
    if ticket_key:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un ticket con esa clave."
        )

    changes = []
    for change in ticket_data.changes:
        component = db.query(Component).filter(
            Component.project_id == project_id,
            Component.id == change.component_id
        ).first()
        if not component:
            raise HTTPException(
                status_code=404,
                detail=f"No existe un componente con el ID '{change.component_id}' en el proyecto {project.name}."
            )

        max_change_number = db.query(func.max(Change.change_number)).filter(Change.component_id == component.id).scalar()

        new_change = Change(
            project_id=project_id,
            component_id=component.id,
            change_number=max_change_number + 1 if max_change_number is not None else 1,
            title=change.title,
            description=change.description,
            cadena=component.cadena,
            step=component.step,
        )
        changes.append(new_change)

    new_ticket = Ticket(
        project_id=project_id,
        ticket_key=ticket_data.ticket_key,
        title=ticket_data.title,
        description=ticket_data.description,
        ticket_url=ticket_data.ticket_url,
        changes = changes
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    return new_ticket

@app.get("/projects/{project_id}/tickets", response_model=list[TicketResponse])
def list_tickets(
    project_id: int,
    db: Session = Depends(get_db)
    ):

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=404,
            detail="No existe un proyecto con ese nombre."
        )

    statement = (
        select(Ticket)
        .where(Ticket.project_id == project_id)
        .order_by(Ticket.id)
        .options(selectinload(Ticket.changes))
    )
    tickets = db.scalars(statement).all()

    return tickets

@app.patch("/tickets/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db)
    ):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="No existe un ticket con ese ID."
        )

    data = ticket_data.model_dump(exclude_unset=True)

    if not data:
        raise HTTPException(
            status_code=400,
            detail="Sin actualización."
        )
    
    changes_to_apply = {key: value for key, value in data.items() if getattr(ticket, key) != value}
    if not changes_to_apply:
        raise HTTPException(
            status_code=400,
            detail="Sin cambios para aplicar."
        )

    if ticket_data.ticket_key is not None:
        exist_ticket = db.query(Ticket).filter(Ticket.ticket_key == ticket_data.ticket_key).first()
        if exist_ticket and exist_ticket.id != ticket_id:
            raise HTTPException(
                status_code=409,
                detail="Ya existe un ticket con esa llave."
            )

    for key, value in changes_to_apply.items():
        setattr(ticket, key, value)

    db.commit()
    db.refresh(ticket)

    return ticket

@app.patch("/change/{change_id}", response_model=ChangeResponse)
def update_change(
    change_id: int,
    change_data: ChangeUpdate,
    db: Session = Depends(get_db)
    ):
    change = db.query(Change).filter(Change.id == change_id).first()
    if not change:
        raise HTTPException(
            status_code=404,
            detail="No existe un cambio con ese ID."
        )

    data = change_data.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(
            status_code=400,
            detail="Sin actualización."
        )

    changes_to_apply = {key: value for key, value in data.items() if getattr(change, key) != value}
    if not changes_to_apply:
        raise HTTPException(
            status_code=400,
            detail="Sin cambios para aplicar."
        )

    if "component_id" in changes_to_apply:
        exist_component = db.query(Component).filter(Component.id == change_data.component_id).first()
        if not exist_component:
            raise HTTPException(
                status_code=404,
                detail="No existe un componente con ese ID."
            )

        if exist_component.project_id != change.project_id:
            raise HTTPException(
                status_code=400,
                detail="El componente no pertenece al mismo proyecto que el cambio."
            )

        max_change_number = db.query(func.max(Change.change_number)).filter(Change.component_id == exist_component.id).scalar()
        change.change_number=max_change_number + 1 if max_change_number is not None else 1
        change.cadena=exist_component.cadena
        change.step=exist_component.step

    for key, value in changes_to_apply.items():
        setattr(change, key, value)

    db.commit()
    db.refresh(change)

    return change

@app.post("/tickets/{ticket_id}", response_model=TicketResponse)
def add_changes_to_ticket(
    ticket_id: int,
    new_changes: list[ChangeCreate],
    db: Session = Depends(get_db)
    ):
    if not new_changes:
        raise HTTPException(
            status_code=400,
            detail="Debe proporcionar al menos un cambio."
        )

    statement = (
        select(Ticket)
        .where(Ticket.id == ticket_id)
        .options(selectinload(Ticket.changes), selectinload(Ticket.project))
    )
    ticket = db.scalars(statement).first()
    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="No existe un ticket con ese ID."
        )

    next_numbers = {}
    changes_to_add = []
    for change_data in new_changes:
        component = db.query(Component).filter(
            Component.project_id == ticket.project_id,
            Component.id == change_data.component_id
        ).first()
        if not component:
            raise HTTPException(
                status_code=404,
                detail=f"No existe un componente con el ID '{change_data.component_id}' en el proyecto {ticket.project.name}."
            )

        if component.id in next_numbers:
            next_number = next_numbers[component.id]
        else:
            max_change_number = db.query(func.max(Change.change_number)).filter(
                Change.component_id == component.id
            ).scalar()

            next_number = max_change_number + 1 if max_change_number is not None else 1

        next_numbers[component.id] = next_number + 1

        new_change = Change(
            project_id=ticket.project_id,
            component_id=component.id,
            change_number=next_number,
            title=change_data.title,
            description=change_data.description,
            cadena=component.cadena,
            step=component.step,
        )
        changes_to_add.append(new_change)

    ticket.changes.extend(changes_to_add)
    db.commit()
    db.refresh(ticket)

    return ticket



