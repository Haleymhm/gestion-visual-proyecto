from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.models import List
from app.schemas.schemas import ListCreate


def create_list(db: Session, list_data: ListCreate, board_id: int) -> List:
    """Crea una nueva lista."""
    # Obtener la posición máxima actual
    max_position = (
        db.query(List)
        .filter(List.boardId == board_id)
        .order_by(desc(List.position))
        .first()
    )
    position = (max_position.position + 1) if max_position else 0

    new_list = List(
        boardId=board_id, title=list_data.title, position=position
    )
    db.add(new_list)
    db.commit()
    db.refresh(new_list)
    return new_list


def get_list_by_id(db: Session, list_id: int) -> List | None:
    """Obtiene una lista por su ID."""
    return db.query(List).filter(List.id == list_id).first()


def get_board_lists(db: Session, board_id: int) -> list[List]:
    """Obtiene todas las listas de un tablero ordenadas por posición."""
    return (
        db.query(List)
        .filter(List.boardId == board_id)
        .order_by(List.position)
        .all()
    )


def update_list(db: Session, list_item: List, **kwargs) -> List:
    """Actualiza una lista."""
    for key, value in kwargs.items():
        if hasattr(list_item, key):
            setattr(list_item, key, value)
    db.add(list_item)
    db.commit()
    db.refresh(list_item)
    return list_item


def delete_list(db: Session, list_id: int) -> bool:
    """Elimina una lista."""
    list_item = get_list_by_id(db, list_id)
    if not list_item:
        return False
    db.delete(list_item)
    db.commit()
    return True


def reorder_lists(db: Session, list_ids: list[int]) -> bool:
    """Reordena las posiciones de las listas."""
    try:
        for position, list_id in enumerate(list_ids):
            list_item = get_list_by_id(db, list_id)
            if list_item:
                list_item.position = position
                db.add(list_item)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
