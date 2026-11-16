from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.change import Change
from app.models.component import Component
from app.schemas.change import ChangeResponse, ChangeUpdate

router = APIRouter()

@router.patch("/change/{change_id}", response_model=ChangeResponse)
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

    for key, value in changes_to_apply.items():
        setattr(change, key, value)

    db.commit()
    db.refresh(change)

    return change
