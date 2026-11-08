from datetime import datetime

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import TypeComponent
from app.models.utils import utc_now


class Component(Base):
    __tablename__ = "components"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Ubicación actual del componente.
    cadena: Mapped[str] = mapped_column(String(150), nullable=False)
    step: Mapped[int] = mapped_column(Integer, nullable=False)
    ref_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    last_modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
    type_component: Mapped[TypeComponent] = mapped_column(
        SqlEnum(
            TypeComponent,
            name="type_component_enum",
            native_enum=False,
            values_callable=lambda enum_type: [member.value for member in enum_type],
        ),
        nullable=False,
        default=TypeComponent.OTHER,
    )
    source_reference: Mapped[str] = mapped_column(Text, nullable=True, default=None)

    project: Mapped["Project"] = relationship(back_populates="components")
    changes: Mapped[list["Change"]] = relationship(back_populates="component")

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "name",
            name="uq_component_project_name",
        ),
    )
