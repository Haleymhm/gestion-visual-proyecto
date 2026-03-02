from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Board(Base):
  __tablename__ = "boards"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  name: Mapped[str] = mapped_column(String(255), nullable=False)
  createdAt: Mapped[datetime] = mapped_column(
    "created_at",
    DateTime(timezone=True),
    default=datetime.utcnow,
    nullable=False,
  )

  lists: Mapped[list["BoardList"]] = relationship(
    "BoardList",
    back_populates="board",
    cascade="all, delete-orphan",
    order_by="BoardList.position",
  )


class BoardList(Base):
  __tablename__ = "board_lists"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  title: Mapped[str] = mapped_column(String(255), nullable=False)
  position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  boardId: Mapped[int] = mapped_column(
    "board_id",
    ForeignKey("boards.id", ondelete="CASCADE"),
    nullable=False,
    index=True,
  )

  board: Mapped["Board"] = relationship("Board", back_populates="lists")
  cards: Mapped[list["Card"]] = relationship(
    "Card",
    back_populates="list",
    cascade="all, delete-orphan",
    order_by="Card.position",
  )


class Card(Base):
  __tablename__ = "cards"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  title: Mapped[str] = mapped_column(String(255), nullable=False)
  description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
  labels: Mapped[str | None] = mapped_column(String(255), nullable=True)
  dueDate: Mapped[datetime | None] = mapped_column(
    "due_date",
    DateTime(timezone=True),
    nullable=True,
  )
  position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  listId: Mapped[int] = mapped_column(
    "list_id",
    ForeignKey("board_lists.id", ondelete="CASCADE"),
    nullable=False,
    index=True,
  )

  list: Mapped["BoardList"] = relationship("BoardList", back_populates="cards")

