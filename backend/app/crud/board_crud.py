from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.models import Board, BoardMember, User, RoleEnum
from app.schemas.schemas import BoardCreate


def create_board(db: Session, board_data: BoardCreate, creator_id: int) -> Board:
    """Crea un nuevo tablero."""
    board = Board(
        title=board_data.title,
        description=board_data.description,
        creatorId=creator_id,
        isPublic=board_data.isPublic,
    )
    db.add(board)
    db.commit()
    db.refresh(board)
    
    # El creador es automáticamente miembro con rol OWNER
    add_board_member(db, board.id, creator_id, RoleEnum.OWNER)
    
    return board


def get_board_by_id(db: Session, board_id: int) -> Board | None:
    """Obtiene un tablero por su ID."""
    return db.query(Board).filter(Board.id == board_id).first()


def get_user_boards(db: Session, user_id: int) -> list[Board]:
    """Obtiene todos los tableros del usuario."""
    return (
        db.query(Board)
        .join(BoardMember, Board.id == BoardMember.boardId)
        .filter(BoardMember.userId == user_id)
        .all()
    )


def update_board(db: Session, board: Board, **kwargs) -> Board:
    """Actualiza un tablero."""
    for key, value in kwargs.items():
        if hasattr(board, key):
            setattr(board, key, value)
    db.add(board)
    db.commit()
    db.refresh(board)
    return board


def delete_board(db: Session, board_id: int) -> bool:
    """Elimina un tablero."""
    board = get_board_by_id(db, board_id)
    if not board:
        return False
    db.delete(board)
    db.commit()
    return True


def add_board_member(
    db: Session,
    board_id: int,
    user_id: int,
    role: RoleEnum = RoleEnum.CONTRIBUTOR,
) -> BoardMember:
    """Añade un miembro a un tablero."""
    member = BoardMember(boardId=board_id, userId=user_id, role=role)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def remove_board_member(db: Session, board_id: int, user_id: int) -> bool:
    """Elimina un miembro de un tablero."""
    member = (
        db.query(BoardMember)
        .filter(and_(BoardMember.boardId == board_id, BoardMember.userId == user_id))
        .first()
    )
    if not member:
        return False
    db.delete(member)
    db.commit()
    return True


def get_board_member(
    db: Session, board_id: int, user_id: int
) -> BoardMember | None:
    """Obtiene un miembro de un tablero."""
    return (
        db.query(BoardMember)
        .filter(and_(BoardMember.boardId == board_id, BoardMember.userId == user_id))
        .first()
    )


def update_board_member_role(
    db: Session, board_id: int, user_id: int, role: RoleEnum
) -> BoardMember | None:
    """Actualiza el rol de un miembro en un tablero."""
    member = get_board_member(db, board_id, user_id)
    if not member:
        return None
    member.role = role
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def get_board_members(db: Session, board_id: int) -> list[BoardMember]:
    """Obtiene todos los miembros de un tablero."""
    return db.query(BoardMember).filter(BoardMember.boardId == board_id).all()
