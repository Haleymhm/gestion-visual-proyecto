from sqlalchemy import Table, Column, ForeignKey
from app.db.base import Base

# Tabla de asociación para Card y Tag (muchos a muchos)
card_tags = Table(
    "card_tags",
    Base.metadata,
    Column("cardId", ForeignKey("cards.id", ondelete="CASCADE"), primary_key=True),
    Column("tagId", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)
