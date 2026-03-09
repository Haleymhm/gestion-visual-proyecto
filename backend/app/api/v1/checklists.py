from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.checklist import Checklist, ChecklistItem
from app.schemas.checklist import ChecklistCreate, ChecklistPublic, ChecklistItemCreate, ChecklistItemPublic, ChecklistItemUpdate

router = APIRouter(
    prefix="/checklists",
    tags=["checklists"],
    dependencies=[Depends(get_current_user)],
)

@router.post("/cards/{card_id}", response_model=ChecklistPublic)
def create_checklist(card_id: int, checklist_in: ChecklistCreate, db: Session = Depends(get_db)):
    db_checklist = Checklist(cardId=card_id, title=checklist_in.title)
    db.add(db_checklist)
    db.commit()
    db.refresh(db_checklist)
    return db_checklist

@router.delete("/{checklist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_checklist(checklist_id: int, db: Session = Depends(get_db)):
    db_checklist = db.get(Checklist, checklist_id)
    if not db_checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")
    db.delete(db_checklist)
    db.commit()

@router.post("/{checklist_id}/items", response_model=ChecklistItemPublic)
def create_checklist_item(checklist_id: int, item_in: ChecklistItemCreate, db: Session = Depends(get_db)):
    db_item = ChecklistItem(checklistId=checklist_id, content=item_in.content, is_completed=item_in.is_completed)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.patch("/items/{item_id}", response_model=ChecklistItemPublic)
def update_checklist_item(item_id: int, item_in: ChecklistItemUpdate, db: Session = Depends(get_db)):
    db_item = db.get(ChecklistItem, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="ChecklistItem not found")
    if item_in.content is not None:
        db_item.content = item_in.content
    if item_in.is_completed is not None:
        db_item.is_completed = item_in.is_completed
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_checklist_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.get(ChecklistItem, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="ChecklistItem not found")
    db.delete(db_item)
    db.commit()
