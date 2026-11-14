from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.utils import utc_now


class Change(Base):
    __tablename__ = "changes"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    component_id: Mapped[int] = mapped_column(ForeignKey("components.id"), index=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), index=True)

    # Numeración consecutiva independiente por componente.
    change_number: Mapped[int] = mapped_column(Integer, nullable=False)

    title: Mapped[str] = mapped_column(String(250))
    description: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    last_modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    component: Mapped["Component"] = relationship(back_populates="changes")
    project: Mapped["Project"] = relationship(back_populates="changes")
    ticket: Mapped["Ticket"] = relationship(back_populates="changes")
    files: Mapped[list["ChangeFile"]] = relationship(
        back_populates="change",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "component_id",
            "change_number",
            name="uq_change_component_number",
        ),
    )
