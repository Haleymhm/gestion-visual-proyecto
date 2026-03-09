import os
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.attachment import Attachment
from app.schemas.attachment import AttachmentPublic

router = APIRouter(
    prefix="/attachments",
    tags=["attachments"],
    dependencies=[Depends(get_current_user)],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/cards/{card_id}", response_model=AttachmentPublic)
def upload_attachment(card_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = UPLOAD_DIR / f"{card_id}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Store relative to allow easy serving if needed
    db_attachment = Attachment(cardId=card_id, file_name=file.filename, file_path=str(file_path))
    db.add(db_attachment)
    db.commit()
    db.refresh(db_attachment)
    return db_attachment

@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attachment(attachment_id: int, db: Session = Depends(get_db)):
    db_attachment = db.get(Attachment, attachment_id)
    if not db_attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    # Remove file from disk
    try:
        if os.path.exists(db_attachment.file_path):
            os.remove(db_attachment.file_path)
    except Exception as e:
        print(f"Failed to delete file {db_attachment.file_path}: {e}")
        
    db.delete(db_attachment)
    db.commit()
