from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class User(Base):
  __tablename__ = "users"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
  fullName: Mapped[str] = mapped_column(
    "full_name",
    String(255),
    nullable=False,
  )
  hashedPassword: Mapped[str] = mapped_column(
    "hashed_password",
    String(255),
    nullable=False,
  )
  createdAt: Mapped[datetime] = mapped_column(
    "created_at",
    DateTime(timezone=True),
    default=datetime.utcnow,
    nullable=False,
  )
  isActive: Mapped[bool] = mapped_column(
    "is_active",
    default=True,
    nullable=False,
  )

  memberships: Mapped[list["BoardMember"]] = relationship(
    "BoardMember",
    back_populates="user",
    cascade="all, delete-orphan",
  )


class BoardMember(Base):
  __tablename__ = "board_members"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  boardId: Mapped[int] = mapped_column(
    "board_id",
    ForeignKey("boards.id", ondelete="CASCADE"),
    nullable=False,
    index=True,
  )
  userId: Mapped[int] = mapped_column(
    "user_id",
    ForeignKey("users.id", ondelete="CASCADE"),
    nullable=False,
    index=True,
  )
  role: Mapped[str] = mapped_column(String(32), nullable=False, default="member")

  user: Mapped["User"] = relationship("User", back_populates="memberships")

