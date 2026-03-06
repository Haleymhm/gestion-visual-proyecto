from pydantic import BaseModel, Field


class ChecklistItemBase(BaseModel):
    content: str = Field(..., max_length=500)
    is_completed: bool = False


class ChecklistItemCreate(ChecklistItemBase):
    pass


class ChecklistItemUpdate(BaseModel):
    content: str | None = Field(None, max_length=500)
    is_completed: bool | None = None


class ChecklistItemPublic(ChecklistItemBase):
    id: int
    checklistId: int

    class Config:
        from_attributes = True


class ChecklistBase(BaseModel):
    title: str = Field(..., max_length=255)


class ChecklistCreate(ChecklistBase):
    pass


class ChecklistUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)


class ChecklistPublic(ChecklistBase):
    id: int
    cardId: int
    items: list[ChecklistItemPublic] = []

    class Config:
        from_attributes = True
