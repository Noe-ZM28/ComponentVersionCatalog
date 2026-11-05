from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    last_modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
    tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="project"
    )
    components: Mapped[list["Component"]] = relationship(
        back_populates="project"
    )
    changes: Mapped[list["Change"]] = relationship(
        back_populates="project"
    )


class Component(Base):
    __tablename__ = "components"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"), index=True
    )
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
    source_type: Mapped[str] = mapped_column(String(30), nullable=False, default="other")
    source_reference: Mapped[str] = mapped_column(Text, nullable=True, default=None)

    project: Mapped["Project"] = relationship(back_populates="components")
    changes: Mapped[list["Change"]] = relationship(
        back_populates="component"
    )

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "name",
            name="uq_component_project_name",
        ),
    )


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_key: Mapped[str] = mapped_column(
        String(100), unique=True, index=True
    )
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"), index=True
    )
    title: Mapped[str] = mapped_column(String(250))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    ticket_url: Mapped[str] = mapped_column(
        String(500), nullable=False
    )
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    changes: Mapped[list["Change"]] = relationship(
        back_populates="ticket"
    )
    project: Mapped["Project"] = relationship(
        back_populates="tickets"
    )


class Change(Base):
    __tablename__ = "changes"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"), index=True
    )
    component_id: Mapped[int] = mapped_column(
        ForeignKey("components.id"), index=True
    )
    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("tickets.id"), index=True
    )

    # Numeración consecutiva independiente por componente.
    change_number: Mapped[int] = mapped_column(Integer, nullable=False)

    title: Mapped[str] = mapped_column(String(250))
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Se conserva la ubicación que tenía el componente al registrar
    # este cambio, aunque su ubicación actual cambie posteriormente.
    cadena: Mapped[str] = mapped_column(String(150), nullable=False)
    step: Mapped[int] = mapped_column(Integer, nullable=False)

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

    component: Mapped["Component"] = relationship(
        back_populates="changes"
    )
    project: Mapped["Project"] = relationship(
        back_populates="changes"
    )
    ticket: Mapped["Ticket"] = relationship(
        back_populates="changes")
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


class FileRecord(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True)
    type_file: Mapped[str] = mapped_column(String(30), nullable=False)

    original_name: Mapped[str] = mapped_column(String(255))
    stored_name: Mapped[str] = mapped_column(
        String(255), unique=True
    )
    storage_path: Mapped[str] = mapped_column(String(1000))

    content_type: Mapped[str] = mapped_column(
        String(150), nullable=False
    )
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), index=True)

    last_modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    changes: Mapped[list["ChangeFile"]] = relationship(
        back_populates="file"
    )


class ChangeFile(Base):
    __tablename__ = "change_files"

    id: Mapped[int] = mapped_column(primary_key=True)

    change_id: Mapped[int] = mapped_column(
        ForeignKey("changes.id"), index=True
    )
    file_id: Mapped[int] = mapped_column(
        ForeignKey("files.id"), index=True
    )

    # Valores previstos: before, after, attachment.
    role: Mapped[str] = mapped_column(String(30), nullable=False)

    description: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    change: Mapped["Change"] = relationship(back_populates="files")
    file: Mapped["FileRecord"] = relationship(back_populates="changes")

