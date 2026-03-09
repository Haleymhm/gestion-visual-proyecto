from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import (
  ACCESS_TOKEN_EXPIRE_MINUTES,
  create_access_token,
  get_password_hash,
  verify_password,
)
from app.crud.user import create_user, get_user_by_email
from app.db.session import get_db
from app.schemas.user import Token, UserCreate, UserPublic

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register_user(
  user_in: UserCreate,
  db: Session = Depends(get_db),
) -> UserPublic:
  user = get_user_by_email(db, email=user_in.email)
  if user:
    raise HTTPException(
      status_code=400,
      detail="The user with this user email already exists in the system.",
    )
  hashed_password = get_password_hash(user_in.password)
  new_user = create_user(
    db,
    email=user_in.email,
    full_name=user_in.fullName,
    hashed_password=hashed_password,
  )
  return new_user


@router.post("/login", response_model=Token)
def login_access_token(
  form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
  db: Session = Depends(get_db),
) -> Token:
  """
  OAuth2 compatible token login, get an access token for future requests
  """
  user = get_user_by_email(db, email=form_data.username)
  if not user or not verify_password(form_data.password, user.hashedPassword):
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Incorrect email or password",
    )
  elif not user.isActive:
    raise HTTPException(status_code=400, detail="Inactive user")

  access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  access_token = create_access_token(
    subject=user.email, expires_delta=access_token_expires
  )
  return Token(access_token=access_token, token_type="bearer")


@router.post("/logout")
def logout() -> dict[str, str]:
  """
  Logout endpoint. In a stateless JWT setup, logout is primarily handled by the 
  client deleting the token. This endpoint exists for API completeness or if 
  token blacklisting were implemented.
  """
  return {"message": "Successfully logged out. Please remove the token from the client."}
