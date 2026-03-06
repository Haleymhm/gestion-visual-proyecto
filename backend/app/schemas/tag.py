from pydantic import BaseModel, Field


class BoardTagBase(BaseModel):
    name: str = Field(..., max_length=255)
    color: str = Field("#e2e8f0", max_length=50)


class BoardTagCreate(BoardTagBase):
    pass


class BoardTagUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    color: str | None = Field(None, max_length=50)


class BoardTagPublic(BoardTagBase):
    id: int
    boardId: int

    class Config:
        from_attributes = True


class CardTagBase(BaseModel):
    tagId: int


class CardTagCreate(CardTagBase):
    pass


class CardTagPublic(CardTagBase):
    id: int
    cardId: int
    tag: BoardTagPublic

    class Config:
        from_attributes = True
