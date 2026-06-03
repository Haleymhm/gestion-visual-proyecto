from datetime import datetime
from sqlalchemy import ForeignKey, String, DateTime, Boolean, Text, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
from app.db.base import Base


class RoleEnum(str, Enum):
    """Enum para roles de usuario en tableros."""
    ADMIN = "admin"
    OWNER = "owner"
    CONTRIBUTOR = "contributor"
    VIEWER = "viewer"


class User(Base):
    """Modelo de usuario."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashedPassword: Mapped[str] = mapped_column(String(255))
    fullName: Mapped[str] = mapped_column(String(255), nullable=True)
    isActive: Mapped[bool] = mapped_column(Boolean, default=True)
    createdAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relaciones
    boards: Mapped[list["Board"]] = relationship(
        "Board", back_populates="creator", foreign_keys="Board.creatorId"
    )
    boardMembers: Mapped[list["BoardMember"]] = relationship(
        "BoardMember", back_populates="user", cascade="all, delete-orphan"
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="author", cascade="all, delete-orphan"
    )


class Board(Base):
    """Modelo de tablero/proyecto."""
    __tablename__ = "boards"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    creatorId: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    isPublic: Mapped[bool] = mapped_column(Boolean, default=False)
    createdAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relaciones
    creator: Mapped["User"] = relationship("User", back_populates="boards")
    members: Mapped[list["BoardMember"]] = relationship(
        "BoardMember", back_populates="board", cascade="all, delete-orphan"
    )
    lists: Mapped[list["List"]] = relationship(
        "List", back_populates="board", cascade="all, delete-orphan"
    )


class BoardMember(Base):
    """Modelo para miembros de un tablero con roles."""
    __tablename__ = "board_members"

    id: Mapped[int] = mapped_column(primary_key=True)
    boardId: Mapped[int] = mapped_column(ForeignKey("boards.id", ondelete="CASCADE"))
    userId: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[RoleEnum] = mapped_column(
        SQLEnum(RoleEnum), default=RoleEnum.CONTRIBUTOR
    )
    joinedAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relaciones
    board: Mapped["Board"] = relationship("Board", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="boardMembers")


class List(Base):
    """Modelo de lista/columna en un tablero."""
    __tablename__ = "lists"

    id: Mapped[int] = mapped_column(primary_key=True)
    boardId: Mapped[int] = mapped_column(ForeignKey("boards.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    position: Mapped[int] = mapped_column(Integer, default=0)
    createdAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relaciones
    board: Mapped["Board"] = relationship("Board", back_populates="lists")
    cards: Mapped[list["Card"]] = relationship(
        "Card", back_populates="list", cascade="all, delete-orphan"
    )


class Card(Base):
    """Modelo de tarjeta/tarea."""
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    listId: Mapped[int] = mapped_column(ForeignKey("lists.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    position: Mapped[int] = mapped_column(Integer, default=0)
    color: Mapped[str] = mapped_column(String(7), default="#FFFFFF")  # Color en hex
    dueDate: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    createdAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relaciones
    list: Mapped["List"] = relationship("List", back_populates="cards")
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="card", cascade="all, delete-orphan"
    )
    checklists: Mapped[list["Checklist"]] = relationship(
        "Checklist", back_populates="card", cascade="all, delete-orphan"
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag", back_populates="cards", secondary="card_tags"
    )


class Comment(Base):
    """Modelo de comentario."""
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    cardId: Mapped[int] = mapped_column(ForeignKey("cards.id", ondelete="CASCADE"))
    authorId: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text)
    createdAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relaciones
    card: Mapped["Card"] = relationship("Card", back_populates="comments")
    author: Mapped["User"] = relationship("User", back_populates="comments")


class Checklist(Base):
    """Modelo de checklist."""
    __tablename__ = "checklists"

    id: Mapped[int] = mapped_column(primary_key=True)
    cardId: Mapped[int] = mapped_column(ForeignKey("cards.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    createdAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relaciones
    card: Mapped["Card"] = relationship("Card", back_populates="checklists")
    items: Mapped[list["ChecklistItem"]] = relationship(
        "ChecklistItem", back_populates="checklist", cascade="all, delete-orphan"
    )


class ChecklistItem(Base):
    """Modelo de elemento en un checklist."""
    __tablename__ = "checklist_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    checklistId: Mapped[int] = mapped_column(
        ForeignKey("checklists.id", ondelete="CASCADE")
    )
    text: Mapped[str] = mapped_column(String(255))
    isCompleted: Mapped[bool] = mapped_column(Boolean, default=False)
    createdAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relaciones
    checklist: Mapped["Checklist"] = relationship("Checklist", back_populates="items")


class Tag(Base):
    """Modelo de etiqueta."""
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    color: Mapped[str] = mapped_column(String(7), default="#FFFFFF")

    # Relaciones
    cards: Mapped[list["Card"]] = relationship(
        "Card", back_populates="tags", secondary="card_tags"
    )
