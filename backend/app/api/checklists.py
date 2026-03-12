from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.models import User, RoleEnum
from app.schemas.schemas import (
    ChecklistCreate,
    ChecklistPublic,
    ChecklistWithItems,
    ChecklistItemCreate,
    ChecklistItemPublic,
)
from app.core.dependencies import get_current_user
from app.crud.board_crud import get_board_by_id, get_board_member
from app.crud.card_crud import get_card_by_id
from app.crud.checklist_crud import (
    create_checklist,
    get_checklist_by_id,
    get_card_checklists,
    update_checklist,
    delete_checklist,
    create_checklist_item,
    get_checklist_item_by_id,
    get_checklist_items,
    update_checklist_item,
    delete_checklist_item,
)
from pydantic import BaseModel

router = APIRouter(
    prefix="/v1/boards/{board_id}/cards/{card_id}/checklists",
    tags=["checklists"],
)


class UpdateChecklistRequest(BaseModel):
    """Schema para actualizar checklist."""
    title: str | None = None


class UpdateChecklistItemRequest(BaseModel):
    """Schema para actualizar item de checklist."""
    text: str | None = None
    isCompleted: bool | None = None


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


# ==================== CHECKLISTS ====================


@router.post("", response_model=ChecklistPublic, status_code=status.HTTP_201_CREATED)
async def create_new_checklist(
    board_id: int,
    card_id: int,
    checklist_data: ChecklistCreate,
    board = Depends(check_contributor_or_higher),
    db: Session = Depends(get_db),
):
    """Crea un nuevo checklist."""
    card = get_card_by_id(db, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarjeta no encontrada",
        )
    
    checklist = create_checklist(db, checklist_data, card_id)
    return checklist


@router.get("", response_model=list[ChecklistWithItems])
async def get_card_checklists_endpoint(
    board_id: int,
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene todos los checklists de una tarjeta."""
    card = get_card_by_id(db, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarjeta no encontrada",
        )
    
    checklists = get_card_checklists(db, card_id)
    result = []
    for checklist in checklists:
        items = get_checklist_items(db, checklist.id)
        result.append({
            **{c: getattr(checklist, c) for c in checklist.__table__.columns.keys()},
            "items": items,
        })
    return result


@router.get("/{checklist_id}", response_model=ChecklistWithItems)
async def get_checklist(
    board_id: int,
    card_id: int,
    checklist_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene un checklist con sus items."""
    card = get_card_by_id(db, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarjeta no encontrada",
        )
    
    checklist = get_checklist_by_id(db, checklist_id)
    if not checklist or checklist.cardId != card_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist no encontrado",
        )
    
    items = get_checklist_items(db, checklist_id)
    return {
        **{c: getattr(checklist, c) for c in checklist.__table__.columns.keys()},
        "items": items,
    }


@router.put("/{checklist_id}", response_model=ChecklistPublic)
async def update_checklist_endpoint(
    board_id: int,
    card_id: int,
    checklist_id: int,
    update_data: UpdateChecklistRequest,
    board = Depends(check_contributor_or_higher),
    db: Session = Depends(get_db),
):
    """Actualiza un checklist."""
    checklist = get_checklist_by_id(db, checklist_id)
    if not checklist or checklist.cardId != card_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist no encontrado",
        )
    
    update_dict = update_data.model_dump(exclude_unset=True)
    checklist = update_checklist(db, checklist, **update_dict)
    return checklist


@router.delete("/{checklist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checklist_endpoint(
    board_id: int,
    card_id: int,
    checklist_id: int,
    board = Depends(check_contributor_or_higher),
    db: Session = Depends(get_db),
):
    """Elimina un checklist."""
    checklist = get_checklist_by_id(db, checklist_id)
    if not checklist or checklist.cardId != card_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist no encontrado",
        )
    
    delete_checklist(db, checklist_id)


# ==================== CHECKLIST ITEMS ====================


@router.post(
    "/{checklist_id}/items",
    response_model=ChecklistItemPublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_checklist_item(
    board_id: int,
    card_id: int,
    checklist_id: int,
    item_data: ChecklistItemCreate,
    board = Depends(check_contributor_or_higher),
    db: Session = Depends(get_db),
):
    """Crea un nuevo item en un checklist."""
    checklist = get_checklist_by_id(db, checklist_id)
    if not checklist or checklist.cardId != card_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist no encontrado",
        )
    
    item = create_checklist_item(db, item_data, checklist_id)
    return item


@router.put(
    "/{checklist_id}/items/{item_id}",
    response_model=ChecklistItemPublic,
)
async def update_checklist_item_endpoint(
    board_id: int,
    card_id: int,
    checklist_id: int,
    item_id: int,
    update_data: UpdateChecklistItemRequest,
    board = Depends(check_contributor_or_higher),
    db: Session = Depends(get_db),
):
    """Actualiza un item de checklist."""
    item = get_checklist_item_by_id(db, item_id)
    if not item or item.checklist.cardId != card_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item no encontrado",
        )
    
    update_dict = update_data.model_dump(exclude_unset=True)
    item = update_checklist_item(db, item, **update_dict)
    return item


@router.delete("/{checklist_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checklist_item_endpoint(
    board_id: int,
    card_id: int,
    checklist_id: int,
    item_id: int,
    board = Depends(check_contributor_or_higher),
    db: Session = Depends(get_db),
):
    """Elimina un item de checklist."""
    item = get_checklist_item_by_id(db, item_id)
    if not item or item.checklist.cardId != card_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item no encontrado",
        )
    
    delete_checklist_item(db, item_id)
