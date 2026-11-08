from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ChangeFile(Base):
    __tablename__ = "change_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    change_id: Mapped[int] = mapped_column(ForeignKey("changes.id"), index=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id"), index=True)

    # Valores previstos: before, after, attachment.
    role: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    change: Mapped["Change"] = relationship(back_populates="files")
    file: Mapped["FileRecord"] = relationship(back_populates="changes")
