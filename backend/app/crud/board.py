from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.crud.activity import log_card_activity
from app.models.board import Board, BoardList, Card
from app.models.checklist import Checklist
from app.models.tag import CardTag
from app.models.user import BoardMember
from app.schemas.board import BoardCreate, BoardListCreate, CardCreate


def _board_load_options():
  return (
    selectinload(Board.tags),
    selectinload(Board.lists)
    .selectinload(BoardList.cards)
    .options(
      selectinload(Card.comments),
      selectinload(Card.checklists).selectinload(Checklist.items),
      selectinload(Card.attachments),
      selectinload(Card.tags).selectinload(CardTag.tag),
    ),
  )


def get_boards(db: Session, user_id: int) -> Sequence[Board]:
  statement = (
    select(Board)
    .join(BoardMember)
    .where(BoardMember.userId == user_id)
    .options(*_board_load_options())
    .order_by(Board.id)
  )
  return db.scalars(statement).unique().all()


def get_board_by_id(db: Session, board_id: int, user_id: int | None = None) -> Board | None:
  statement = (
    select(Board)
    .options(*_board_load_options())
    .where(Board.id == board_id)
  )
  
  if user_id is not None:
    statement = statement.join(BoardMember).where(BoardMember.userId == user_id)
    
  return db.scalar(statement)


def move_card_between_lists(
  db: Session,
  *,
  board_id: int,
  user_id: int,
  card_id: int,
  dest_list_id: int,
  dest_index: int,
) -> Board:
  card = db.get(Card, card_id)
  if card is None:
    msg = "Card not found"
    raise ValueError(msg)

  # Use the card's actual listId from the DB as the source (source of truth)
  source_list_id = card.listId

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
    list(source_cards)
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

  board = get_board_by_id(db, board_id=board_id, user_id=user_id)
  if board is None:
    msg = "Board not found after card move"
    raise ValueError(msg)
  return board

def create_board(db: Session, payload: BoardCreate, user_id: int) -> Board:
  board = Board(name=payload.name, createdAt=datetime.utcnow())
  db.add(board)
  db.flush() # Flush to get board.id
  
  # Create the user membership association
  membership = BoardMember(
    boardId=board.id,
    userId=user_id,
    role="owner"
  )
  db.add(membership)
  db.commit()
  db.refresh(board)
  return board


def delete_board(db: Session, board_id: int, user_id: int) -> None:
  board = get_board_by_id(db, board_id, user_id)
  if board is None:
    msg = "Board not found or access denied"
    raise ValueError(msg)
  db.delete(board)
  db.commit()


def create_list(db: Session, board_id: int, user_id: int, payload: BoardListCreate) -> Board:
  board = get_board_by_id(db, board_id, user_id)
  if board is None:
    msg = "Board not found or access denied"
    raise ValueError(msg)
  max_pos = max((lst.position for lst in board.lists), default=-1)
  new_list = BoardList(title=payload.title, position=max_pos + 1, boardId=board_id)
  db.add(new_list)
  db.commit()
  board = get_board_by_id(db, board_id, user_id)
  if board is None:
    raise ValueError("Board not found after commit")
  return board


def delete_list(db: Session, board_id: int, user_id: int, list_id: int) -> None:
  board = get_board_by_id(db, board_id, user_id)
  if board is None:
    msg = "Board not found or access denied"
    raise ValueError(msg)
  lst = db.get(BoardList, list_id)
  if lst is None or lst.boardId != board_id:
    msg = "List not found"
    raise ValueError(msg)
  db.delete(lst)
  db.commit()


def create_card(db: Session, board_id: int, user_id: int, list_id: int, payload: CardCreate) -> Board:
  board = get_board_by_id(db, board_id, user_id)
  if board is None:
    msg = "Board not found or access denied"
    raise ValueError(msg)
  lst = db.get(BoardList, list_id)
  if lst is None or lst.boardId != board_id:
    msg = "List not found"
    raise ValueError(msg)
  # Calculate next position
  stmt = select(Card).where(Card.listId == list_id).order_by(Card.position)
  existing = list(db.scalars(stmt))
  max_pos = max((c.position for c in existing), default=-1)
  card = Card(
    title=payload.title,
    description=payload.description,
    position=max_pos + 1,
    listId=list_id,
  )
  db.add(card)
  db.commit()
  board = get_board_by_id(db, board_id, user_id)
  if board is None:
    raise ValueError("Board not found after commit")
  return board


def delete_card(db: Session, board_id: int, user_id: int, card_id: int) -> None:
  board = get_board_by_id(db, board_id, user_id)
  if board is None:
    msg = "Board not found or access denied"
    raise ValueError(msg)
  card = db.get(Card, card_id)
  if card is None:
    msg = "Card not found"
    raise ValueError(msg)
  lst = db.get(BoardList, card.listId)
  if lst is None or lst.boardId != board_id:
    msg = "Card does not belong to the specified board"
    raise ValueError(msg)
  db.delete(card)
  db.commit()
