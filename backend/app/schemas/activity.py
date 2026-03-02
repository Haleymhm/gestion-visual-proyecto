from datetime import datetime

from pydantic import BaseModel


class CardActivityPublic(BaseModel):
  id: int
  cardId: int
  type: str
  payload: str | None
  createdAt: datetime

  class Config:
    from_attributes = True

