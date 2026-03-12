from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.base import get_db
from app.schemas.schemas import UserCreate, UserPublic
from app.crud.user_crud import (
    create_user,
    get_user_by_email,
    authenticate_user,
)
from app.core.security import create_access_token
from app.core.config import settings
from app.core.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/v1/auth", tags=["auth"])


class LoginRequest(BaseModel):
    """Schema para login."""
    email: str
    password: str


class TokenResponse(BaseModel):
    """Schema para respuesta de token."""
    access_token: str
    token_type: str


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registra un nuevo usuario."""
    # Verificar si el usuario ya existe
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado",
        )
    
    user = create_user(db, user_data)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest, db: Session = Depends(get_db)
):
    """Inicia sesión con email y contraseña."""
    user = authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña inválidos",
        )
    
    # Crear token JWT
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserPublic)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Obtiene la información del usuario actual."""
    return current_user
