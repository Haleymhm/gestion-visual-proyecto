from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.models import User, RoleEnum
from app.schemas.schemas import TagCreate, TagPublic
from app.core.dependencies import get_current_user
from app.crud.board_crud import get_board_by_id, get_board_member
from app.crud.card_crud import get_card_by_id
from app.crud.tag_crud import (
    create_tag,
    get_tag_by_id,
    get_all_tags,
    update_tag,
    delete_tag,
    add_tag_to_card,
    remove_tag_from_card,
)
from pydantic import BaseModel

router = APIRouter(prefix="/v1/boards/{board_id}/cards/{card_id}/tags", tags=["tags"])


class UpdateTagRequest(BaseModel):
    """Schema para actualizar etiqueta."""
    name: str | None = None
    color: str | None = None


class AddTagRequest(BaseModel):
    """Schema para añadir etiqueta a tarjeta."""
    tagId: int


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


@router.post("", response_model=TagPublic, status_code=status.HTTP_201_CREATED)
async def create_new_tag(
    board_id: int,
    card_id: int,
    tag_data: TagCreate,
    board = Depends(check_contributor_or_higher),
    db: Session = Depends(get_db),
):
    """Crea una nueva etiqueta global."""
    tag = create_tag(db, tag_data)
    return tag


@router.get("", response_model=list[TagPublic])
async def get_all_tags_endpoint(
    board_id: int,
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene todas las etiquetas."""
    tags = get_all_tags(db)
    return tags


@router.post("/add-to-card", response_model=TagPublic, status_code=status.HTTP_201_CREATED)
async def add_tag_to_card_endpoint(
    board_id: int,
    card_id: int,
    add_tag_data: AddTagRequest,
    board = Depends(check_contributor_or_higher),
    db: Session = Depends(get_db),
):
    """Añade una etiqueta a una tarjeta."""
    card = get_card_by_id(db, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarjeta no encontrada",
        )
    
    card = add_tag_to_card(db, card_id, add_tag_data.tagId)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Etiqueta no encontrada",
        )
    
    tag = get_tag_by_id(db, add_tag_data.tagId)
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tag_from_card_endpoint(
    board_id: int,
    card_id: int,
    tag_id: int,
    board = Depends(check_contributor_or_higher),
    db: Session = Depends(get_db),
):
    """Elimina una etiqueta de una tarjeta."""
    card = get_card_by_id(db, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarjeta no encontrada",
        )
    
    card = remove_tag_from_card(db, card_id, tag_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Etiqueta no encontrada",
        )
