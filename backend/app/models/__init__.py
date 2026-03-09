# Import all models here so that Base.metadata.create_all() and SQLAlchemy
# relationship string resolution (e.g. relationship("BoardTag")) work
# consistently across the app.

from app.models.user import User, BoardMember
from app.models.board import Board, BoardList, Card
from app.models.tag import BoardTag, CardTag
from app.models.checklist import Checklist, ChecklistItem
from app.models.comment import Comment
from app.models.attachment import Attachment
from app.models.activity import CardActivity

__all__ = [
    "User",
    "BoardMember",
    "Board",
    "BoardList",
    "Card",
    "BoardTag",
    "CardTag",
    "Checklist",
    "ChecklistItem",
    "Comment",
    "Attachment",
    "CardActivity",
]
