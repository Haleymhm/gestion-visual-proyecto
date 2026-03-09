from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.user import BoardMember, User


def get_users(db: Session, *, skip: int = 0, limit: int = 100) -> Iterable[User]:
  statement = select(User).offset(skip).limit(limit)
  return db.scalars(statement).all()


def get_user_by_email(db: Session, *, email: str) -> User | None:
  statement = select(User).where(User.email == email)
  return db.scalar(statement)


def create_user(
  db: Session,
  *,
  email: str,
  full_name: str,
  hashed_password: str,
) -> User:
  user = User(
    email=email,
    fullName=full_name,
    hashedPassword=hashed_password,
  )
  db.add(user)
  db.commit()
  db.refresh(user)
  return user


def get_board_members(
  db: Session,
  *,
  board_id: int,
) -> Iterable[BoardMember]:
  statement = (
    select(BoardMember)
    .options(joinedload(BoardMember.user))
    .where(BoardMember.boardId == board_id)
  )
  return db.scalars(statement).unique().all()

