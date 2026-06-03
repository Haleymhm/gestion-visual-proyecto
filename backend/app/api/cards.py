from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.models import User, RoleEnum
from app.schemas.schemas import CardCreate, CardPublic, CardWithDetails
from app.core.dependencies import get_current_user
from app.crud.board_crud import get_board_by_id, get_board_member
from app.crud.list_crud import get_list_by_id
from app.crud.card_crud import (
    create_card,
    get_card_by_id,
    get_list_cards,
    update_card,
    delete_card,
    move_card,
    reorder_cards,
)
from app.crud.comment_crud import get_card_comments
from app.crud.checklist_crud import get_card_checklists
from pydantic import BaseModel

router = APIRouter(prefix="/v1/boards/{board_id}/lists/{list_id}/cards", tags=["cards"])


class UpdateCardRequest(BaseModel):
    """Schema para actualizar tarjeta."""
    title: str | None = None
    description: str | None = None
    color: str | None = None
    dueDate: str | None = None
    position: int | None = None


class MoveCardRequest(BaseModel):
    """Schema para mover tarjeta."""
    newListId: int
    newPosition: int


class ReorderCardsRequest(BaseModel):
    """Schema para reordenar tarjetas."""
    cardIds: list[int]


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


@router.post("", response_model=CardPublic, status_code=status.HTTP_201_CREATED)
async def create_new_card(
    board_id: int,
    list_id: int,
    card_data: CardCreate,
    board = Depends(check_contributor_or_higher),
    db: Session = Depends(get_db),
):
    """Crea una nueva tarjeta."""
    list_item = get_list_by_id(db, list_id)
    if not list_item or list_item.boardId != board_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lista no encontrada",
        )
    
    card = create_card(db, card_data, list_id)
    return card


@router.get("", response_model=list[CardPublic])
async def get_list_cards_endpoint(
    board_id: int,
    list_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene todas las tarjetas de una lista."""
    list_item = get_list_by_id(db, list_id)
    if not list_item or list_item.boardId != board_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lista no encontrada",
        )
    
    cards = get_list_cards(db, list_id)
    return cards


@router.get("/{card_id}", response_model=CardWithDetails)
async def get_card(
    board_id: int,
    list_id: int,
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene una tarjeta con todos sus detalles."""
    list_item = get_list_by_id(db, list_id)
    if not list_item or list_item.boardId != board_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lista no encontrada",
        )
    
    card = get_card_by_id(db, card_id)
    if not card or card.listId != list_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarjeta no encontrada",
        )
    
    comments = get_card_comments(db, card_id)
    checklists = get_card_checklists(db, card_id)
    
    return {
        **{c: getattr(card, c) for c in card.__table__.columns.keys()},
        "comments": comments,
        "checklists": checklists,
        "tags": card.tags,
    }


@router.put("/{card_id}", response_model=CardPublic)
async def update_card_endpoint(
    board_id: int,
    list_id: int,
    card_id: int,
    update_data: UpdateCardRequest,
    board = Depends(check_contributor_or_higher),
    db: Session = Depends(get_db),
):
    """Actualiza una tarjeta."""
    card = get_card_by_id(db, card_id)
    if not card or card.listId != list_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarjeta no encontrada",
        )
    
    update_dict = update_data.model_dump(exclude_unset=True)
    card = update_card(db, card, **update_dict)
    return card


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card_endpoint(
    board_id: int,
    list_id: int,
    card_id: int,
    board = Depends(check_contributor_or_higher),
    db: Session = Depends(get_db),
):
    """Elimina una tarjeta."""
    card = get_card_by_id(db, card_id)
    if not card or card.listId != list_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarjeta no encontrada",
        )
    
    delete_card(db, card_id)


@router.post("/{card_id}/move", response_model=CardPublic)
async def move_card_endpoint(
    board_id: int,
    list_id: int,
    card_id: int,
    move_data: MoveCardRequest,
    board = Depends(check_contributor_or_higher),
    db: Session = Depends(get_db),
):
    """Mueve una tarjeta a otra lista."""
    card = get_card_by_id(db, card_id)
    if not card or card.listId != list_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarjeta no encontrada",
        )
    
    moved_card = move_card(db, card_id, move_data.newListId, move_data.newPosition)
    if not moved_card:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al mover la tarjeta",
        )
    
    return moved_card


@router.post("/reorder", status_code=status.HTTP_200_OK)
async def reorder_cards_endpoint(
    board_id: int,
    list_id: int,
    reorder_data: ReorderCardsRequest,
    board = Depends(check_contributor_or_higher),
    db: Session = Depends(get_db),
):
    """Reordena las tarjetas de una lista."""
    success = reorder_cards(db, reorder_data.cardIds)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al reordenar las tarjetas",
        )
    return {"message": "Tarjetas reordenadas correctamente"}
