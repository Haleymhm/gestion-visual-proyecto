from collections.abc import Sequence

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user

from app.crud.activity import get_card_activity
from app.db.session import get_db
from app.schemas.activity import CardActivityPublic


router = APIRouter(
  prefix="/activity",
  tags=["activity"],
  dependencies=[Depends(get_current_user)],
)


@router.get(
  "/cards/{card_id}",
  response_model=list[CardActivityPublic],
  status_code=status.HTTP_200_OK,
  summary="Get recent activity for a card",
)
async def list_card_activity(
  card_id: int,
  db: Session = Depends(get_db),
) -> Sequence[CardActivityPublic]:
  activity = get_card_activity(db, card_id=card_id)
  return activity

