from datetime import datetime

from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    content: str | None = None


class CommentPublic(CommentBase):
    id: int
    cardId: int
    createdAt: datetime
    userId: int | None = None

    class Config:
        from_attributes = True
