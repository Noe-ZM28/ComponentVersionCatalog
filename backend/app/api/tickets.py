from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.change import Change
from app.models.component import Component
from app.models.project import Project
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate
from app.schemas.change import ChangeCreate

router = APIRouter()

@router.post("/projects/{project_id}/tickets", response_model=TicketResponse, status_code=201)
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
    next_numbers = {}
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

        if component.id in next_numbers:
            change_number = next_numbers[component.id]
        else:
            max_change_number = db.query(func.max(Change.change_number)).filter(
                Change.component_id == component.id
            ).scalar()
            change_number = max_change_number + 1 if max_change_number is not None else 1

        next_numbers[component.id] = change_number + 1
        new_change = Change(
            project_id=project_id,
            component_id=component.id,
            change_number=change_number,
            title=change.title,
            description=change.description,
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

@router.get("/projects/{project_id}/tickets", response_model=list[TicketResponse])
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

@router.patch("/tickets/{ticket_id}", response_model=TicketResponse)
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

@router.post("/tickets/{ticket_id}", response_model=TicketResponse)
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
        )
        changes_to_add.append(new_change)

    ticket.changes.extend(changes_to_add)
    db.commit()
    db.refresh(ticket)

    return ticket
