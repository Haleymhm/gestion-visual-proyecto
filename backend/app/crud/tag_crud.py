from sqlalchemy.orm import Session
from app.models.models import Tag, Card
from app.schemas.schemas import TagCreate


def create_tag(db: Session, tag_data: TagCreate) -> Tag:
    """Crea una nueva etiqueta."""
    tag = Tag(name=tag_data.name, color=tag_data.color)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def get_tag_by_id(db: Session, tag_id: int) -> Tag | None:
    """Obtiene una etiqueta por su ID."""
    return db.query(Tag).filter(Tag.id == tag_id).first()


def get_tag_by_name(db: Session, name: str) -> Tag | None:
    """Obtiene una etiqueta por su nombre."""
    return db.query(Tag).filter(Tag.name == name).first()


def get_all_tags(db: Session) -> list[Tag]:
    """Obtiene todas las etiquetas."""
    return db.query(Tag).all()


def update_tag(db: Session, tag: Tag, **kwargs) -> Tag:
    """Actualiza una etiqueta."""
    for key, value in kwargs.items():
        if hasattr(tag, key):
            setattr(tag, key, value)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def delete_tag(db: Session, tag_id: int) -> bool:
    """Elimina una etiqueta."""
    tag = get_tag_by_id(db, tag_id)
    if not tag:
        return False
    db.delete(tag)
    db.commit()
    return True


def add_tag_to_card(db: Session, card_id: int, tag_id: int) -> Card | None:
    """Añade una etiqueta a una tarjeta."""
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        return None
    
    tag = get_tag_by_id(db, tag_id)
    if not tag:
        return None
    
    if tag not in card.tags:
        card.tags.append(tag)
        db.add(card)
        db.commit()
        db.refresh(card)
    
    return card


def remove_tag_from_card(db: Session, card_id: int, tag_id: int) -> Card | None:
    """Elimina una etiqueta de una tarjeta."""
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        return None
    
    tag = get_tag_by_id(db, tag_id)
    if not tag:
        return None
    
    if tag in card.tags:
        card.tags.remove(tag)
        db.add(card)
        db.commit()
        db.refresh(card)
    
    return card
