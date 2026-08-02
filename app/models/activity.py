from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    start_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    end_time: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    process_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    window_title: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    def __repr__(self) -> str:
        return (
            f"Activity(id={self.id!r}, "
            f"process_name={self.process_name!r}, "
            f"start_time={self.start_time!r})"
        )
