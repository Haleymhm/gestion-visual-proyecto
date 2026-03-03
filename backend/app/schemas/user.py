from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
  email: EmailStr
  fullName: str = Field(..., max_length=255)


class UserCreate(UserBase):
  password: str = Field(..., min_length=8, max_length=128)


class UserPublic(UserBase):
  id: int
  createdAt: datetime
  isActive: bool

  class Config:
    from_attributes = True


class BoardMemberPublic(BaseModel):
  id: int
  boardId: int
  userId: int
  role: str
  user: UserPublic

  class Config:
    from_attributes = True


class Token(BaseModel):
  access_token: str
  token_type: str


class TokenData(BaseModel):
  email: str | None = None
