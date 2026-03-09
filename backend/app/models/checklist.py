from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Checklist(Base):
    __tablename__ = "checklists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    cardId: Mapped[int] = mapped_column(
        "card_id",
        ForeignKey("cards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    card: Mapped["Card"] = relationship("Card", back_populates="checklists")
    items: Mapped[list["ChecklistItem"]] = relationship(
        "ChecklistItem",
        back_populates="checklist",
        cascade="all, delete-orphan",
        order_by="ChecklistItem.id",
    )


class ChecklistItem(Base):
    __tablename__ = "checklist_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    checklistId: Mapped[int] = mapped_column(
        "checklist_id",
        ForeignKey("checklists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    checklist: Mapped["Checklist"] = relationship("Checklist", back_populates="items")
