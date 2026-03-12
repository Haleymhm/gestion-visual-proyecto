from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.models import Card
from app.schemas.schemas import CardCreate


def create_card(db: Session, card_data: CardCreate, list_id: int) -> Card:
    """Crea una nueva tarjeta."""
    # Obtener la posición máxima actual
    max_position = (
        db.query(Card)
        .filter(Card.listId == list_id)
        .order_by(desc(Card.position))
        .first()
    )
    position = (max_position.position + 1) if max_position else 0

    card = Card(
        listId=list_id,
        title=card_data.title,
        description=card_data.description,
        color=card_data.color,
        dueDate=card_data.dueDate,
        position=position,
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


def get_card_by_id(db: Session, card_id: int) -> Card | None:
    """Obtiene una tarjeta por su ID."""
    return db.query(Card).filter(Card.id == card_id).first()


def get_list_cards(db: Session, list_id: int) -> list[Card]:
    """Obtiene todas las tarjetas de una lista ordenadas por posición."""
    return (
        db.query(Card)
        .filter(Card.listId == list_id)
        .order_by(Card.position)
        .all()
    )


def update_card(db: Session, card: Card, **kwargs) -> Card:
    """Actualiza una tarjeta."""
    for key, value in kwargs.items():
        if hasattr(card, key):
            setattr(card, key, value)
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


def delete_card(db: Session, card_id: int) -> bool:
    """Elimina una tarjeta."""
    card = get_card_by_id(db, card_id)
    if not card:
        return False
    db.delete(card)
    db.commit()
    return True


def move_card(db: Session, card_id: int, new_list_id: int, new_position: int) -> Card | None:
    """Mueve una tarjeta a otra lista y posición."""
    card = get_card_by_id(db, card_id)
    if not card:
        return None
    
    card.listId = new_list_id
    card.position = new_position
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


def reorder_cards(db: Session, card_ids: list[int]) -> bool:
    """Reordena las posiciones de las tarjetas en una lista."""
    try:
        for position, card_id in enumerate(card_ids):
            card = get_card_by_id(db, card_id)
            if card:
                card.position = position
                db.add(card)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
