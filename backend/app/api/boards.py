from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.models import User, RoleEnum
from app.schemas.schemas import (
    BoardCreate,
    BoardPublic,
    BoardWithLists,
    BoardMemberPublic,
    ListPublic,
)
from app.core.dependencies import get_current_user
from app.crud.board_crud import (
    create_board,
    get_board_by_id,
    get_user_boards,
    update_board,
    delete_board,
    add_board_member,
    remove_board_member,
    get_board_member,
    update_board_member_role,
    get_board_members,
)
from app.crud.list_crud import get_board_lists
from pydantic import BaseModel

router = APIRouter(prefix="/v1/boards", tags=["boards"])


class UpdateBoardRequest(BaseModel):
    """Schema para actualizar tablero."""
    title: str | None = None
    description: str | None = None
    isPublic: bool | None = None


class AddMemberRequest(BaseModel):
    """Schema para añadir miembro a tablero."""
    userId: int
    role: RoleEnum = RoleEnum.CONTRIBUTOR


class UpdateMemberRoleRequest(BaseModel):
    """Schema para actualizar rol de miembro."""
    role: RoleEnum


def check_board_access(
    board_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Verifica que el usuario tenga acceso al tablero."""
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


def check_board_owner_or_admin(
    board_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Verifica que el usuario sea propietario o admin del tablero."""
    board = get_board_by_id(db, board_id)
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tablero no encontrado",
        )
    
    member = get_board_member(db, board_id, current_user.id)
    if not member or member.role not in [RoleEnum.OWNER, RoleEnum.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para esta acción",
        )
    
    return board


@router.post("", response_model=BoardPublic, status_code=status.HTTP_201_CREATED)
async def create_new_board(
    board_data: BoardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Crea un nuevo tablero."""
    board = create_board(db, board_data, current_user.id)
    return board


@router.get("/my-boards", response_model=list[BoardPublic])
async def get_my_boards(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene todos los tableros del usuario."""
    boards = get_user_boards(db, current_user.id)
    return boards


@router.get("/{board_id}", response_model=BoardWithLists)
async def get_board(
    board_id: int,
    board: dict = Depends(check_board_access),
    db: Session = Depends(get_db),
):
    """Obtiene un tablero con sus listas."""
    lists = get_board_lists(db, board_id)
    return {
        **{c: getattr(board, c) for c in board.__table__.columns.keys()},
        "lists": lists,
    }


@router.put("/{board_id}", response_model=BoardPublic)
async def update_board_info(
    board_id: int,
    update_data: UpdateBoardRequest,
    board: dict = Depends(check_board_owner_or_admin),
    db: Session = Depends(get_db),
):
    """Actualiza un tablero."""
    update_dict = update_data.model_dump(exclude_unset=True)
    board = update_board(db, board, **update_dict)
    return board


@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board_endpoint(
    board_id: int,
    board: dict = Depends(check_board_owner_or_admin),
    db: Session = Depends(get_db),
):
    """Elimina un tablero."""
    delete_board(db, board_id)


@router.post("/{board_id}/members", response_model=BoardMemberPublic, status_code=status.HTTP_201_CREATED)
async def add_member_to_board(
    board_id: int,
    member_data: AddMemberRequest,
    board: dict = Depends(check_board_owner_or_admin),
    db: Session = Depends(get_db),
):
    """Añade un miembro al tablero."""
    # Verificar que el usuario no sea ya miembro
    existing_member = get_board_member(db, board_id, member_data.userId)
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya es miembro del tablero",
        )
    
    member = add_board_member(db, board_id, member_data.userId, member_data.role)
    return member


@router.get("/{board_id}/members", response_model=list[BoardMemberPublic])
async def get_board_members_endpoint(
    board_id: int,
    board: dict = Depends(check_board_access),
    db: Session = Depends(get_db),
):
    """Obtiene los miembros del tablero."""
    members = get_board_members(db, board_id)
    return members


@router.put("/{board_id}/members/{user_id}", response_model=BoardMemberPublic)
async def update_member_role(
    board_id: int,
    user_id: int,
    role_data: UpdateMemberRoleRequest,
    board: dict = Depends(check_board_owner_or_admin),
    db: Session = Depends(get_db),
):
    """Actualiza el rol de un miembro."""
    member = update_board_member_role(db, board_id, user_id, role_data.role)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Miembro no encontrado",
        )
    return member


@router.delete("/{board_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member_from_board(
    board_id: int,
    user_id: int,
    board: dict = Depends(check_board_owner_or_admin),
    db: Session = Depends(get_db),
):
    """Elimina un miembro del tablero."""
    success = remove_board_member(db, board_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Miembro no encontrado",
        )
