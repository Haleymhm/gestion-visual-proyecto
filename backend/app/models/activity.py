from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class CardActivity(Base):
  __tablename__ = "card_activity"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  cardId: Mapped[int] = mapped_column(
    "card_id",
    ForeignKey("cards.id", ondelete="CASCADE"),
    nullable=False,
    index=True,
  )
  type: Mapped[str] = mapped_column(String(64), nullable=False)
  payload: Mapped[str | None] = mapped_column(Text, nullable=True)
  createdAt: Mapped[datetime] = mapped_column(
    "created_at",
    DateTime(timezone=True),
    default=datetime.utcnow,
    nullable=False,
  )

