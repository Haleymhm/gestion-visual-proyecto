from datetime import datetime

from pydantic import BaseModel, Field


class AttachmentBase(BaseModel):
    file_name: str = Field(..., max_length=255)


class AttachmentCreate(AttachmentBase):
    # Depending on how we upload, file_path might be set internally.
    # Usually we don't allow clients to set file_path directly.
    pass


class AttachmentPublic(AttachmentBase):
    id: int
    cardId: int
    file_path: str
    uploadedAt: datetime

    class Config:
        from_attributes = True
