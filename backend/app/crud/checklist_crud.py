from sqlalchemy.orm import Session
from app.models.models import Checklist, ChecklistItem
from app.schemas.schemas import ChecklistCreate, ChecklistItemCreate


def create_checklist(
    db: Session, checklist_data: ChecklistCreate, card_id: int
) -> Checklist:
    """Crea un nuevo checklist."""
    checklist = Checklist(cardId=card_id, title=checklist_data.title)
    db.add(checklist)
    db.commit()
    db.refresh(checklist)
    return checklist


def get_checklist_by_id(db: Session, checklist_id: int) -> Checklist | None:
    """Obtiene un checklist por su ID."""
    return db.query(Checklist).filter(Checklist.id == checklist_id).first()


def get_card_checklists(db: Session, card_id: int) -> list[Checklist]:
    """Obtiene todos los checklists de una tarjeta."""
    return db.query(Checklist).filter(Checklist.cardId == card_id).all()


def update_checklist(db: Session, checklist: Checklist, **kwargs) -> Checklist:
    """Actualiza un checklist."""
    for key, value in kwargs.items():
        if hasattr(checklist, key):
            setattr(checklist, key, value)
    db.add(checklist)
    db.commit()
    db.refresh(checklist)
    return checklist


def delete_checklist(db: Session, checklist_id: int) -> bool:
    """Elimina un checklist."""
    checklist = get_checklist_by_id(db, checklist_id)
    if not checklist:
        return False
    db.delete(checklist)
    db.commit()
    return True


# ==================== CHECKLIST ITEMS ====================


def create_checklist_item(
    db: Session,
    item_data: ChecklistItemCreate,
    checklist_id: int,
) -> ChecklistItem:
    """Crea un nuevo elemento en un checklist."""
    item = ChecklistItem(
        checklistId=checklist_id,
        text=item_data.text,
        isCompleted=item_data.isCompleted,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_checklist_item_by_id(db: Session, item_id: int) -> ChecklistItem | None:
    """Obtiene un elemento de checklist por su ID."""
    return db.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()


def get_checklist_items(db: Session, checklist_id: int) -> list[ChecklistItem]:
    """Obtiene todos los elementos de un checklist."""
    return db.query(ChecklistItem).filter(ChecklistItem.checklistId == checklist_id).all()


def update_checklist_item(
    db: Session, item: ChecklistItem, **kwargs
) -> ChecklistItem:
    """Actualiza un elemento de checklist."""
    for key, value in kwargs.items():
        if hasattr(item, key):
            setattr(item, key, value)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def delete_checklist_item(db: Session, item_id: int) -> bool:
    """Elimina un elemento de checklist."""
    item = get_checklist_item_by_id(db, item_id)
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True
