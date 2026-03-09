from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.security import ALGORITHM, SECRET_KEY
from app.crud.user import get_user_by_email
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import TokenData


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def get_current_user(
  token: Annotated[str, Depends(oauth2_scheme)],
  db: Annotated[Session, Depends(get_db)],
) -> User:
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
  )
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email: str = payload.get("sub")
    if email is None:
      raise credentials_exception
    token_data = TokenData(email=email)
  except JWTError:
    raise credentials_exception

  user = get_user_by_email(db, email=token_data.email)
  if user is None:
    raise credentials_exception
  if not user.isActive:
    raise HTTPException(status_code=400, detail="Inactive user")
  return user
