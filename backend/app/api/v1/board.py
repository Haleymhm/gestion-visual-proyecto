import logging
from collections.abc import Sequence

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.websockets import WebSocketDisconnect
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.models.user import User

from app.crud.board import (
  create_board,
  create_card,
  create_list,
  delete_board,
  delete_card,
  delete_list,
  get_boards,
  move_card_between_lists,
)
from app.db.session import get_db
from app.schemas.board import (
  BoardCreate,
  BoardPublic,
  CardCreate,
  CardCreateRequest,
  CardMoveRequest,
)


router = APIRouter(
  prefix="/boards",
  tags=["boards"],
  dependencies=[Depends(get_current_user)],
)


@router.get(
  "",
  response_model=list[BoardPublic],
  summary="List boards with lists and cards",
)
async def list_boards(
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> Sequence[BoardPublic]:
  try:
    boards = get_boards(db=db, user_id=current_user.id)
    return boards
  except Exception as exc:
    logging.exception("list_boards failed for user_id=%s: %s", current_user.id, exc)
    raise


@router.post(
  "",
  response_model=BoardPublic,
  status_code=status.HTTP_201_CREATED,
  summary="Create a new board",
)
async def create_board_endpoint(
  payload: BoardCreate,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> BoardPublic:
  board = create_board(db, payload, current_user.id)
  return board


@router.delete(
  "/{board_id}",
  status_code=status.HTTP_204_NO_CONTENT,
  summary="Delete a board",
)
async def delete_board_endpoint(
  board_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> None:
  try:
    delete_board(db, board_id, current_user.id)
  except ValueError as exc:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
  "/{board_id}/lists",
  response_model=BoardPublic,
  status_code=status.HTTP_201_CREATED,
  summary="Add a list (column) to a board",
)
async def create_list_endpoint(
  board_id: int,
  payload: BoardCreate,  # reuse name-only schema
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> BoardPublic:
  from app.schemas.board import BoardListCreate
  try:
    board = create_list(db, board_id, current_user.id, BoardListCreate(title=payload.name, position=0, boardId=board_id))
  except ValueError as exc:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
  return board


@router.delete(
  "/{board_id}/lists/{list_id}",
  status_code=status.HTTP_204_NO_CONTENT,
  summary="Delete a list from a board",
)
async def delete_list_endpoint(
  board_id: int,
  list_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> None:
  try:
    delete_list(db, board_id, current_user.id, list_id)
  except ValueError as exc:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
  "/{board_id}/lists/{list_id}/cards",
  response_model=BoardPublic,
  status_code=status.HTTP_201_CREATED,
  summary="Add a card to a list",
)
async def create_card_endpoint(
  board_id: int,
  list_id: int,
  payload: CardCreateRequest,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> BoardPublic:
  try:
    full_payload = CardCreate(
      title=payload.title,
      description=payload.description,
      labels=[],
      dueDate=None,
      position=0,
      listId=list_id,
    )
    board = create_card(db, board_id, current_user.id, list_id, full_payload)
  except ValueError as exc:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
  return board


@router.delete(
  "/{board_id}/cards/{card_id}",
  status_code=status.HTTP_204_NO_CONTENT,
  summary="Delete a card from a board",
)
async def delete_card_endpoint(
  board_id: int,
  card_id: int,
  db: Session = Depends(get_db),
) -> None:
  try:
    delete_card(db, board_id, card_id)
  except ValueError as exc:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
  "/{board_id}/move-card",
  response_model=BoardPublic,
  status_code=status.HTTP_200_OK,
  summary="Move a card between lists and reorder positions",
)
async def move_card(
  board_id: int,
  payload: CardMoveRequest,
  request: Request,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
) -> BoardPublic:
  try:
    board = move_card_between_lists(
      db,
      board_id=board_id,
      user_id=current_user.id,
      card_id=payload.cardId,
      dest_list_id=payload.destListId,
      dest_index=payload.destIndex,
    )
  except ValueError as exc:
    logging.warning(
      "move-card 400: board=%s payload=%s error=%s",
      board_id,
      {
        "cardId": payload.cardId,
        "destListId": payload.destListId,
        "destIndex": payload.destIndex,
      },
      exc,
    )
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail=str(exc),
    ) from exc

  payload_json = jsonable_encoder(board)
  if payload.notify_clients:
    connections = request.app.state.board_connections.get(board_id, set())
    for websocket in list(connections):
      try:
        await websocket.send_json(payload_json)
      except WebSocketDisconnect:
        connections.remove(websocket)

  return board
