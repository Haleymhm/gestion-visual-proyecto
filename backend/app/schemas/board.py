from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.checklist import ChecklistPublic
from app.schemas.comment import CommentPublic
from app.schemas.attachment import AttachmentPublic
from app.schemas.tag import CardTagPublic, BoardTagPublic


class CardBase(BaseModel):
  title: str = Field(..., max_length=255)
  description: str | None = Field(None, max_length=2000)
  labels: list[str] = Field(default_factory=list)
  dueDate: datetime | None = None
  position: int
  listId: int

  @field_validator("labels", mode="before")
  @classmethod
  def parse_labels(cls, v: str | list[str] | None) -> list[str]:
    if isinstance(v, str):
      return [label.strip() for label in v.split(",") if label.strip()]
    return v or []


class CardCreate(CardBase):
  pass


class CardCreateRequest(BaseModel):
  """Simplified schema for creating a card via the REST API (position/listId inferred server-side)."""
  title: str = Field(..., max_length=255)
  description: str | None = Field(None, max_length=2000)


class CardUpdate(BaseModel):
  title: str | None = Field(None, max_length=255)
  description: str | None = Field(None, max_length=2000)
  labels: list[str] | None = None
  dueDate: datetime | None = None
  position: int | None = None
  listId: int | None = None


class CardPublic(CardBase):
  id: int
  checklists: list[ChecklistPublic] = []
  comments: list[CommentPublic] = []
  attachments: list[AttachmentPublic] = []
  tags: list[CardTagPublic] = []

  @field_validator("checklists", "comments", "attachments", "tags", mode="before")
  @classmethod
  def ensure_list(cls, v: list | None) -> list:
    if v is None:
      return []
    if isinstance(v, list):
      return v
    return [v]

  class Config:
    from_attributes = True


class CardMoveRequest(BaseModel):
  cardId: int
  destListId: int
  destIndex: int
  sourceListId: int | None = None  # Optional; backend uses card.listId as source
  notify_clients: bool = True


class BoardListBase(BaseModel):
  title: str = Field(..., max_length=255)
  position: int
  boardId: int


class BoardListCreate(BoardListBase):
  pass


class BoardListUpdate(BaseModel):
  title: str | None = Field(None, max_length=255)
  position: int | None = None


class BoardListPublic(BoardListBase):
  id: int
  cards: list[CardPublic] = []

  class Config:
    from_attributes = True


class BoardBase(BaseModel):
  name: str = Field(..., max_length=255)


class BoardCreate(BoardBase):
  pass


class BoardUpdate(BaseModel):
  name: str | None = Field(None, max_length=255)


class BoardPublic(BoardBase):
  id: int
  createdAt: datetime
  lists: list[BoardListPublic] = []
  tags: list[BoardTagPublic] = []

  class Config:
    from_attributes = True

