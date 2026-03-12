from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.models import User, RoleEnum
from app.schemas.schemas import ListCreate, ListPublic, ListWithCards
from app.core.dependencies import get_current_user
from app.crud.board_crud import get_board_by_id, get_board_member
from app.crud.list_crud import (
    create_list,
    get_list_by_id,
    get_board_lists,
    update_list,
    delete_list,
    reorder_lists,
)
from app.crud.card_crud import get_list_cards
from pydantic import BaseModel

router = APIRouter(prefix="/v1/boards/{board_id}/lists", tags=["lists"])


class UpdateListRequest(BaseModel):
    """Schema para actualizar lista."""
    title: str | None = None
    position: int | None = None


class ReorderListsRequest(BaseModel):
    """Schema para reordenar listas."""
    listIds: list[int]


def check_board_member(
    board_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Verifica que el usuario sea miembro del tablero."""
    board = get_board_by_id(db, board_id)
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tablero no encontrado",
        )
    
    member = get_board_member(db, board_id, current_user.id)
    if not member and not board.isPublic:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a este tablero",
        )
    
    return board


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


@router.post("", response_model=ListPublic, status_code=status.HTTP_201_CREATED)
async def create_new_list(
    board_id: int,
    list_data: ListCreate,
    board = Depends(check_contributor_or_higher),
    db: Session = Depends(get_db),
):
    """Crea una nueva lista."""
    new_list = create_list(db, list_data, board_id)
    return new_list


@router.get("", response_model=list[ListWithCards])
async def get_board_lists_endpoint(
    board_id: int,
    board = Depends(check_board_member),
    db: Session = Depends(get_db),
):
    """Obtiene todas las listas del tablero con sus tarjetas."""
    lists = get_board_lists(db, board_id)
    result = []
    for list_item in lists:
        cards = get_list_cards(db, list_item.id)
        result.append({
            **{c: getattr(list_item, c) for c in list_item.__table__.columns.keys()},
            "cards": cards,
        })
    return result


@router.get("/{list_id}", response_model=ListWithCards)
async def get_list(
    board_id: int,
    list_id: int,
    board = Depends(check_board_member),
    db: Session = Depends(get_db),
):
    """Obtiene una lista con sus tarjetas."""
    list_item = get_list_by_id(db, list_id)
    if not list_item or list_item.boardId != board_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lista no encontrada",
        )
    
    cards = get_list_cards(db, list_id)
    return {
        **{c: getattr(list_item, c) for c in list_item.__table__.columns.keys()},
        "cards": cards,
    }


@router.put("/{list_id}", response_model=ListPublic)
async def update_list_endpoint(
    board_id: int,
    list_id: int,
    update_data: UpdateListRequest,
    board = Depends(check_contributor_or_higher),
    db: Session = Depends(get_db),
):
    """Actualiza una lista."""
    list_item = get_list_by_id(db, list_id)
    if not list_item or list_item.boardId != board_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lista no encontrada",
        )
    
    update_dict = update_data.model_dump(exclude_unset=True)
    list_item = update_list(db, list_item, **update_dict)
    return list_item


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_list_endpoint(
    board_id: int,
    list_id: int,
    board = Depends(check_contributor_or_higher),
    db: Session = Depends(get_db),
):
    """Elimina una lista."""
    list_item = get_list_by_id(db, list_id)
    if not list_item or list_item.boardId != board_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lista no encontrada",
        )
    
    delete_list(db, list_id)


@router.post("/reorder", status_code=status.HTTP_200_OK)
async def reorder_lists_endpoint(
    board_id: int,
    reorder_data: ReorderListsRequest,
    board = Depends(check_contributor_or_higher),
    db: Session = Depends(get_db),
):
    """Reordena las listas del tablero."""
    success = reorder_lists(db, reorder_data.listIds)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al reordenar las listas",
        )
    return {"message": "Listas reordenadas correctamente"}
