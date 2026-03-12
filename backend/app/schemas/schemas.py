from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from app.models.models import RoleEnum


# ==================== USER SCHEMAS ====================

class UserBase(BaseModel):
    """Schema base para Usuario."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    fullName: Optional[str] = None


class UserCreate(UserBase):
    """Schema para creación de Usuario."""
    password: str = Field(..., min_length=8)


class UserPublic(UserBase):
    """Schema de respuesta para Usuario."""
    id: int
    isActive: bool
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


# ==================== BOARD SCHEMAS ====================

class BoardBase(BaseModel):
    """Schema base para Tablero."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    isPublic: bool = False


class BoardCreate(BoardBase):
    """Schema para creación de Tablero."""
    pass


class BoardPublic(BoardBase):
    """Schema de respuesta para Tablero."""
    id: int
    creatorId: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class BoardWithLists(BoardPublic):
    """Schema de Tablero con sus Listas."""
    lists: list["ListPublic"] = []


# ==================== BOARD MEMBER SCHEMAS ====================

class BoardMemberBase(BaseModel):
    """Schema base para Miembro de Tablero."""
    userId: int
    role: RoleEnum = RoleEnum.CONTRIBUTOR


class BoardMemberCreate(BoardMemberBase):
    """Schema para creación de Miembro de Tablero."""
    pass


class BoardMemberPublic(BoardMemberBase):
    """Schema de respuesta para Miembro de Tablero."""
    id: int
    boardId: int
    joinedAt: datetime

    class Config:
        from_attributes = True


# ==================== LIST SCHEMAS ====================

class ListBase(BaseModel):
    """Schema base para Lista."""
    title: str = Field(..., min_length=1, max_length=255)
    position: int = 0


class ListCreate(ListBase):
    """Schema para creación de Lista."""
    pass


class ListPublic(ListBase):
    """Schema de respuesta para Lista."""
    id: int
    boardId: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class ListWithCards(ListPublic):
    """Schema de Lista con sus Tarjetas."""
    cards: list["CardPublic"] = []


# ==================== TAG SCHEMAS ====================

class TagBase(BaseModel):
    """Schema base para Etiqueta."""
    name: str = Field(..., min_length=1, max_length=100)
    color: str = "#FFFFFF"


class TagCreate(TagBase):
    """Schema para creación de Etiqueta."""
    pass


class TagPublic(TagBase):
    """Schema de respuesta para Etiqueta."""
    id: int

    class Config:
        from_attributes = True


# ==================== CHECKLIST ITEM SCHEMAS ====================

class ChecklistItemBase(BaseModel):
    """Schema base para Elemento de Checklist."""
    text: str = Field(..., min_length=1, max_length=255)
    isCompleted: bool = False


class ChecklistItemCreate(ChecklistItemBase):
    """Schema para creación de Elemento de Checklist."""
    pass


class ChecklistItemPublic(ChecklistItemBase):
    """Schema de respuesta para Elemento de Checklist."""
    id: int
    checklistId: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


# ==================== CHECKLIST SCHEMAS ====================

class ChecklistBase(BaseModel):
    """Schema base para Checklist."""
    title: str = Field(..., min_length=1, max_length=255)


class ChecklistCreate(ChecklistBase):
    """Schema para creación de Checklist."""
    pass


class ChecklistPublic(ChecklistBase):
    """Schema de respuesta para Checklist."""
    id: int
    cardId: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class ChecklistWithItems(ChecklistPublic):
    """Schema de Checklist con sus Items."""
    items: list[ChecklistItemPublic] = []


# ==================== COMMENT SCHEMAS ====================

class CommentBase(BaseModel):
    """Schema base para Comentario."""
    content: str = Field(..., min_length=1)


class CommentCreate(CommentBase):
    """Schema para creación de Comentario."""
    pass


class CommentPublic(CommentBase):
    """Schema de respuesta para Comentario."""
    id: int
    cardId: int
    authorId: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class CommentWithAuthor(CommentPublic):
    """Schema de Comentario con datos del autor."""
    author: UserPublic


# ==================== CARD SCHEMAS ====================

class CardBase(BaseModel):
    """Schema base para Tarjeta."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    position: int = 0
    color: str = "#FFFFFF"
    dueDate: Optional[datetime] = None


class CardCreate(CardBase):
    """Schema para creación de Tarjeta."""
    pass


class CardPublic(CardBase):
    """Schema de respuesta para Tarjeta."""
    id: int
    listId: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


class CardWithDetails(CardPublic):
    """Schema de Tarjeta con todos sus detalles."""
    comments: list[CommentWithAuthor] = []
    checklists: list[ChecklistWithItems] = []
    tags: list[TagPublic] = []


# Update schemas forward references
BoardWithLists.model_rebuild()
ListWithCards.model_rebuild()
ChecklistWithItems.model_rebuild()
CardWithDetails.model_rebuild()
