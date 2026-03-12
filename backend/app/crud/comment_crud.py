from sqlalchemy.orm import Session
from app.models.models import Comment
from app.schemas.schemas import CommentCreate


def create_comment(
    db: Session, comment_data: CommentCreate, card_id: int, author_id: int
) -> Comment:
    """Crea un nuevo comentario."""
    comment = Comment(
        cardId=card_id, authorId=author_id, content=comment_data.content
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def get_comment_by_id(db: Session, comment_id: int) -> Comment | None:
    """Obtiene un comentario por su ID."""
    return db.query(Comment).filter(Comment.id == comment_id).first()


def get_card_comments(db: Session, card_id: int) -> list[Comment]:
    """Obtiene todos los comentarios de una tarjeta."""
    return db.query(Comment).filter(Comment.cardId == card_id).all()


def update_comment(db: Session, comment: Comment, **kwargs) -> Comment:
    """Actualiza un comentario."""
    for key, value in kwargs.items():
        if hasattr(comment, key):
            setattr(comment, key, value)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(db: Session, comment_id: int) -> bool:
    """Elimina un comentario."""
    comment = get_comment_by_id(db, comment_id)
    if not comment:
        return False
    db.delete(comment)
    db.commit()
    return True
