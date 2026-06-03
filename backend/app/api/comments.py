from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.models import User, RoleEnum
from app.schemas.schemas import CommentCreate, CommentPublic, CommentWithAuthor
from app.core.dependencies import get_current_user
from app.crud.board_crud import get_board_by_id, get_board_member
from app.crud.card_crud import get_card_by_id
from app.crud.comment_crud import (
    create_comment,
    get_comment_by_id,
    get_card_comments,
    update_comment,
    delete_comment,
)
from pydantic import BaseModel

router = APIRouter(prefix="/v1/boards/{board_id}/cards/{card_id}/comments", tags=["comments"])


class UpdateCommentRequest(BaseModel):
    """Schema para actualizar comentario."""
    content: str


def check_contributor_or_higher(
    board_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Verifica que el usuario sea contribuidor o superior."""
    board = get_board_by_id(db, board_id)
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tablero no encontrado",
        )
    
    member = get_board_member(db, board_id, current_user.id)
    if not member or member.role == RoleEnum.VIEWER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para esta acción",
        )
    
    return board


@router.post("", response_model=CommentWithAuthor, status_code=status.HTTP_201_CREATED)
async def create_new_comment(
    board_id: int,
    card_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    board = Depends(check_contributor_or_higher),
    db: Session = Depends(get_db),
):
    """Crea un nuevo comentario."""
    card = get_card_by_id(db, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarjeta no encontrada",
        )
    
    comment = create_comment(db, comment_data, card_id, current_user.id)
    return {
        **{c: getattr(comment, c) for c in comment.__table__.columns.keys()},
        "author": current_user,
    }


@router.get("", response_model=list[CommentWithAuthor])
async def get_card_comments_endpoint(
    board_id: int,
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene todos los comentarios de una tarjeta."""
    card = get_card_by_id(db, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarjeta no encontrada",
        )
    
    comments = get_card_comments(db, card_id)
    return comments


@router.put("/{comment_id}", response_model=CommentPublic)
async def update_comment_endpoint(
    board_id: int,
    card_id: int,
    comment_id: int,
    update_data: UpdateCommentRequest,
    current_user: User = Depends(get_current_user),
    board = Depends(check_contributor_or_higher),
    db: Session = Depends(get_db),
):
    """Actualiza un comentario."""
    card = get_card_by_id(db, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarjeta no encontrada",
        )
    
    comment = get_comment_by_id(db, comment_id)
    if not comment or comment.cardId != card_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario no encontrado",
        )
    
    # Verificar que el usuario sea el autor del comentario
    if comment.authorId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes editar un comentario que no es tuyo",
        )
    
    comment = update_comment(db, comment, content=update_data.content)
    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment_endpoint(
    board_id: int,
    card_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_user),
    board = Depends(check_contributor_or_higher),
    db: Session = Depends(get_db),
):
    """Elimina un comentario."""
    card = get_card_by_id(db, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarjeta no encontrada",
        )
    
    comment = get_comment_by_id(db, comment_id)
    if not comment or comment.cardId != card_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario no encontrado",
        )
    
    # Verificar que el usuario sea el autor del comentario
    if comment.authorId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes eliminar un comentario que no es tuyo",
        )
    
    delete_comment(db, comment_id)
