from pydantic import BaseModel, Field, field_validator


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

    @field_validator("items", mode="before")
    @classmethod
    def ensure_items_list(cls, v: list | None) -> list:
        if v is None:
            return []
        if isinstance(v, list):
            return v
        return []

    class Config:
        from_attributes = True
