from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentPublic, CommentUpdate
from app.models.user import User

router = APIRouter(
    prefix="/comments",
    tags=["comments"],
    dependencies=[Depends(get_current_user)],
)

@router.post("/cards/{card_id}", response_model=CommentPublic)
def create_comment(card_id: int, comment_in: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_comment = Comment(cardId=card_id, content=comment_in.content, userId=current_user.id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.patch("/{comment_id}", response_model=CommentPublic)
def update_comment(comment_id: int, comment_in: CommentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_comment = db.get(Comment, comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.userId != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this comment")
    if comment_in.content is not None:
        db_comment.content = comment_in.content
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_comment = db.get(Comment, comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    # Add check for board owner / admin too if required, but for now just author
    if db_comment.userId != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    db.delete(db_comment)
    db.commit()
