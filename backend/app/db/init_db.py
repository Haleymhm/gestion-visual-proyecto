from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import Base, engine, SessionLocal
from app.models.board import Board, BoardList, Card
from app.models.user import BoardMember, User


def init_db() -> None:
  Base.metadata.create_all(bind=engine)

  db: Session = SessionLocal()
  try:
    existing_board = db.scalar(select(Board).limit(1))
    existing_user = db.scalar(select(User).limit(1))
    if existing_board is not None and existing_user is not None:
      return

    owner = existing_user
    if owner is None:
      owner = User(
        email="admin@example.com",
        fullName="Admin User",
        hashedPassword="not-used-yet",
      )
      db.add(owner)
      db.flush()

    board = Board(name="Team roadmap")
    db.add(board)
    db.flush()

    todo_list = BoardList(title="To Do", position=0, boardId=board.id)
    in_progress_list = BoardList(
      title="In Progress",
      position=1,
      boardId=board.id,
    )
    done_list = BoardList(title="Done", position=2, boardId=board.id)
    db.add_all([todo_list, in_progress_list, done_list])
    db.flush()

    cards: list[Card] = [
      Card(
        title="Design login page",
        description="Create responsive layout and empty state",
        labels="design",
        position=0,
        listId=todo_list.id,
      ),
      Card(
        title="Define user roles",
        description="Admin, member and guest permissions",
        labels="product",
        position=1,
        listId=todo_list.id,
      ),
      Card(
        title="Implement Kanban board",
        description="Columns, cards and drag & drop logic",
        labels="frontend",
        position=0,
        listId=in_progress_list.id,
      ),
      Card(
        title="Set up project",
        description="Create frontend workspace with Next.js",
        labels="chore",
        position=0,
        listId=done_list.id,
      ),
    ]

    db.add_all(cards)

    membership = BoardMember(
      boardId=board.id,
      userId=owner.id,
      role="owner",
    )
    db.add(membership)
    db.commit()
  finally:
    db.close()

