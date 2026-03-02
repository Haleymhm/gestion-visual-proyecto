from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import CardActivity


def log_card_activity(
  db: Session,
  *,
  card_id: int,
  activity_type: str,
  payload: str | None = None,
) -> CardActivity:
  activity = CardActivity(
    cardId=card_id,
    type=activity_type,
    payload=payload,
  )
  db.add(activity)
  db.flush()
  return activity


def get_card_activity(
  db: Session,
  *,
  card_id: int,
  limit: int = 50,
) -> Sequence[CardActivity]:
  statement = (
    select(CardActivity)
    .where(CardActivity.cardId == card_id)
    .order_by(CardActivity.createdAt.desc())
    .limit(limit)
  )
  return db.scalars(statement).all()

