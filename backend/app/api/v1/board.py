from collections.abc import Sequence

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.websockets import WebSocketDisconnect
from sqlalchemy.orm import Session

from app.crud.board import get_boards, move_card_between_lists
from app.db.session import get_db
from app.schemas.board import BoardPublic, CardMoveRequest


router = APIRouter(prefix="/boards", tags=["boards"])


@router.get(
  "",
  response_model=list[BoardPublic],
  summary="List boards with lists and cards",
)
async def list_boards(
  db: Session = Depends(get_db),
) -> Sequence[BoardPublic]:
  boards = get_boards(db=db)
  return boards


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
) -> BoardPublic:
  try:
    board = move_card_between_lists(
      db,
      board_id=board_id,
      card_id=payload.cardId,
      source_list_id=payload.sourceListId,
      dest_list_id=payload.destListId,
      dest_index=payload.destIndex,
    )
  except ValueError as exc:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail=str(exc),
    ) from exc

  payload_json = jsonable_encoder(board)
  connections = request.app.state.board_connections.get(board_id, set())
  for websocket in list(connections):
    try:
      await websocket.send_json(payload_json)
    except WebSocketDisconnect:
      connections.remove(websocket)

  return board

