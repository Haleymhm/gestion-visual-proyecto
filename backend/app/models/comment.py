from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    createdAt: Mapped[datetime] = mapped_column(
        "created_at",
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    
    # Ideally should link to a User, but for now we might leave it optional if no users
    # Or link to User model if present.
    userId: Mapped[int | None] = mapped_column(
        "user_id", ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    
    cardId: Mapped[int] = mapped_column(
        "card_id",
        ForeignKey("cards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    card: Mapped["Card"] = relationship("Card", back_populates="comments")
    # user: Mapped["User"] = relationship("User") # Assuming User model exists
