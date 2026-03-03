from collections.abc import Sequence

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user

from app.crud.user import get_board_members, get_users
from app.db.session import get_db
from app.schemas.user import BoardMemberPublic, UserPublic


router = APIRouter(
  prefix="/users",
  tags=["users"],
  dependencies=[Depends(get_current_user)],
)


@router.get(
  "",
  response_model=list[UserPublic],
  status_code=status.HTTP_200_OK,
  summary="List all users",
)
async def list_users(
  skip: int = 0,
  limit: int = 100,
  db: Session = Depends(get_db),
) -> Sequence[UserPublic]:
  users = get_users(db, skip=skip, limit=limit)
  return users


@router.get(
  "/boards/{board_id}/members",
  response_model=list[BoardMemberPublic],
  status_code=status.HTTP_200_OK,
  summary="List users and roles for a board",
)
async def list_board_members(
  board_id: int,
  db: Session = Depends(get_db),
) -> Sequence[BoardMemberPublic]:
  members = get_board_members(db, board_id=board_id)
  return members

