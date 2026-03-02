from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.crud.activity import log_card_activity
from app.models.board import Board, BoardList, Card


def get_boards(db: Session) -> Sequence[Board]:
  statement = select(Board).options(
    joinedload(Board.lists).joinedload(BoardList.cards),
  ).order_by(Board.id)
  return db.scalars(statement).unique().all()


def get_board_by_id(db: Session, board_id: int) -> Board | None:
  statement = (
    select(Board)
    .options(
      joinedload(Board.lists).joinedload(BoardList.cards),
    )
    .where(Board.id == board_id)
  )
  return db.scalar(statement)


def move_card_between_lists(
  db: Session,
  *,
  board_id: int,
  card_id: int,
  source_list_id: int,
  dest_list_id: int,
  dest_index: int,
) -> Board:
  card = db.get(Card, card_id)
  if card is None:
    msg = "Card not found"
    raise ValueError(msg)

  if card.listId != source_list_id:
    msg = "Card does not belong to source list"
    raise ValueError(msg)

  source_list = db.get(BoardList, source_list_id)
  dest_list = db.get(BoardList, dest_list_id)

  if source_list is None or dest_list is None:
    msg = "Source or destination list not found"
    raise ValueError(msg)

  if source_list.boardId != board_id or dest_list.boardId != board_id:
    msg = "Lists do not belong to the specified board"
    raise ValueError(msg)

  source_cards_stmt = (
    select(Card)
    .where(Card.listId == source_list_id)
    .order_by(Card.position)
  )
  dest_cards_stmt = (
    select(Card).where(Card.listId == dest_list_id).order_by(Card.position)
  )

  source_cards = list(db.scalars(source_cards_stmt))
  dest_cards = (
    source_cards
    if source_list_id == dest_list_id
    else list(db.scalars(dest_cards_stmt))
  )

  try:
    moving_index = next(
      index for index, c in enumerate(source_cards) if c.id == card_id
    )
  except StopIteration as exc:
    msg = "Card not found in source list"
    raise ValueError(msg) from exc

  moving_card = source_cards.pop(moving_index)

  if source_list_id == dest_list_id:
    dest_cards = source_cards

  insert_index = max(0, min(dest_index, len(dest_cards)))
  dest_cards.insert(insert_index, moving_card)

  if source_list_id != dest_list_id:
    moving_card.listId = dest_list_id

  for index, card_in_list in enumerate(source_cards):
    card_in_list.position = index

  if dest_cards is not source_cards:
    for index, card_in_list in enumerate(dest_cards):
      card_in_list.position = index

  log_card_activity(
    db,
    card_id=card_id,
    activity_type="move",
    payload=(
      f"from_list={source_list_id};to_list={dest_list_id};"
      f"to_index={dest_index}"
    ),
  )

  db.commit()

  board = get_board_by_id(db, board_id=board_id)
  if board is None:
    msg = "Board not found after card move"
    raise ValueError(msg)
  return board

