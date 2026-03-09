from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class BoardTag(Base):
    __tablename__ = "board_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    color: Mapped[str] = mapped_column(String(50), nullable=False, default="#e2e8f0")
    boardId: Mapped[int] = mapped_column(
        "board_id",
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    board: Mapped["Board"] = relationship("Board", back_populates="tags")
    # cards relationship mapped in Card via CardTag
    card_tags: Mapped[list["CardTag"]] = relationship(
        "CardTag",
        back_populates="tag",
        cascade="all, delete-orphan",
    )


class CardTag(Base):
    __tablename__ = "card_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cardId: Mapped[int] = mapped_column(
        "card_id",
        ForeignKey("cards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tagId: Mapped[int] = mapped_column(
        "tag_id",
        ForeignKey("board_tags.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    card: Mapped["Card"] = relationship("Card", back_populates="tags")
    tag: Mapped["BoardTag"] = relationship("BoardTag", back_populates="card_tags")
