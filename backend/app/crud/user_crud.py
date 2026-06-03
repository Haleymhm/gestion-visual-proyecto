from sqlalchemy.orm import Session
from app.models.models import User
from app.schemas.schemas import UserCreate
from app.core.security import hash_password, verify_password


def create_user(db: Session, user_data: UserCreate) -> User:
    """Crea un nuevo usuario."""
    user = User(
        email=user_data.email,
        username=user_data.username,
        fullName=user_data.fullName,
        hashedPassword=hash_password(user_data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    """Obtiene un usuario por su email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    """Obtiene un usuario por su username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Obtiene un usuario por su ID."""
    return db.query(User).filter(User.id == user_id).first()


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Autentica un usuario con email y contraseña."""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashedPassword):
        return None
    return user


def update_user(db: Session, user: User, **kwargs) -> User:
    """Actualiza un usuario."""
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def deactivate_user(db: Session, user: User) -> User:
    """Desactiva un usuario."""
    user.isActive = False
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
