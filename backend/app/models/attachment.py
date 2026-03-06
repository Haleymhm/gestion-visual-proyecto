from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    uploadedAt: Mapped[datetime] = mapped_column(
        "uploaded_at",
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    
    cardId: Mapped[int] = mapped_column(
        "card_id",
        ForeignKey("cards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    card: Mapped["Card"] = relationship("Card", back_populates="attachments")
