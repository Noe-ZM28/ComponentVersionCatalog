from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.utils import utc_now


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    cust_num: Mapped[int | None] = mapped_column(Integer, unique=True, index=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="project")
    components: Mapped[list["Component"]] = relationship(back_populates="project")
    changes: Mapped[list["Change"]] = relationship(back_populates="project")
