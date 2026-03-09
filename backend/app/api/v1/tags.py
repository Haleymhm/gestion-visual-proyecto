from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.tag import BoardTag, CardTag
from app.schemas.tag import BoardTagCreate, BoardTagUpdate, BoardTagPublic, CardTagPublic, CardTagCreate

router = APIRouter(
    prefix="/tags",
    tags=["tags"],
    dependencies=[Depends(get_current_user)],
)

@router.post("/boards/{board_id}", response_model=BoardTagPublic)
def create_board_tag(board_id: int, tag_in: BoardTagCreate, db: Session = Depends(get_db)):
    db_tag = BoardTag(boardId=board_id, name=tag_in.name, color=tag_in.color)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@router.delete("/boards/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_board_tag(tag_id: int, db: Session = Depends(get_db)):
    db_tag = db.get(BoardTag, tag_id)
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(db_tag)
    db.commit()

@router.post("/cards/{card_id}", response_model=CardTagPublic)
def add_tag_to_card(card_id: int, tag_in: CardTagCreate, db: Session = Depends(get_db)):
    db_card_tag = CardTag(cardId=card_id, tagId=tag_in.tagId)
    db.add(db_card_tag)
    db.commit()
    db.refresh(db_card_tag)
    return db_card_tag

@router.delete("/cards/{card_tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_tag_from_card(card_tag_id: int, db: Session = Depends(get_db)):
    db_card_tag = db.get(CardTag, card_tag_id)
    if not db_card_tag:
        raise HTTPException(status_code=404, detail="CardTag not found")
    db.delete(db_card_tag)
    db.commit()
