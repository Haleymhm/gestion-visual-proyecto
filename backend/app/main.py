from collections import defaultdict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.activity import router as activity_router
from app.api.v1.auth import router as auth_router
from app.api.v1.board import router as board_router
from app.api.v1.user import router as user_router
from app.api.v1.tags import router as tags_router
from app.api.v1.checklists import router as checklists_router
from app.api.v1.comments import router as comments_router
from app.api.v1.attachments import router as attachments_router
from app.db.init_db import init_db
import app.models  # Import all models to ensure SQLAlchemy mapper registry is complete



def create_app() -> FastAPI:
  app = FastAPI(
    title="Kanban Visual API",
    version="0.1.0",
  )

  app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
  )

  app.state.board_connections = defaultdict(set)

  app.include_router(auth_router, prefix="/api/v1")
  app.include_router(board_router, prefix="/api/v1")
  app.include_router(user_router, prefix="/api/v1")
  app.include_router(activity_router, prefix="/api/v1")
  app.include_router(tags_router, prefix="/api/v1")
  app.include_router(checklists_router, prefix="/api/v1")
  app.include_router(comments_router, prefix="/api/v1")
  app.include_router(attachments_router, prefix="/api/v1")

  app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

  @app.on_event("startup")
  async def on_startup() -> None:
    # Ensure uploads directory exists
    import os
    os.makedirs("uploads", exist_ok=True)
    init_db()

  @app.get("/", include_in_schema=False)
  async def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")

  @app.get("/api/v1/health", tags=["health"])
  async def health_check() -> dict[str, str]:
    return {"status": "ok"}

  @app.websocket("/ws/boards/{board_id}")
  async def board_updates(websocket: WebSocket, board_id: int) -> None:
    await websocket.accept()
    connections = websocket.app.state.board_connections[board_id]
    connections.add(websocket)
    try:
      while True:
        await websocket.receive_text()
    except WebSocketDisconnect:
      connections.remove(websocket)

  return app


app = create_app()

