# API Usage Guide (FastAPI backend)

Base URL (local dev):
- HTTP: http://127.0.0.1:8000
- WebSocket: ws://127.0.0.1:8000

All REST endpoints are prefixed with: /api/v1

--------------------------------
GET /api/v1/boards
--------------------------------
Description:
- Returns all boards with their lists and cards.

Response 200 (JSON example, trimmed):
[
  {
    "id": 1,
    "name": "Team roadmap",
    "createdAt": "2026-03-02T10:00:00Z",
    "lists": [
      {
        "id": 1,
        "title": "To Do",
        "position": 0,
        "boardId": 1,
        "cards": [
          {
            "id": 1,
            "title": "Design login page",
            "description": "Create responsive layout and empty state",
            "labels": ["design"],
            "dueDate": null,
            "position": 0,
            "listId": 1
          }
        ]
      }
    ]
  }
]

--------------------------------
POST /api/v1/boards/{board_id}/move-card
--------------------------------
Description:
- Moves a card between lists or reorders it inside the same list.
- Persists the new positions and broadcasts the updated board via WebSocket.

Path params:
- board_id (int): Board identifier.

Request body (JSON):
{
  "cardId": 1,
  "sourceListId": 1,
  "destListId": 2,
  "destIndex": 0
}

Response 200:
- Returns the updated Board object (same shape as GET /boards).

--------------------------------
GET /api/v1/users/boards/{board_id}/members
--------------------------------
Description:
- Returns the users and their roles for a given board.

Path params:
- board_id (int)

Response 200 (example):
[
  {
    "id": 1,
    "boardId": 1,
    "userId": 1,
    "role": "owner",
    "user": {
      "id": 1,
      "email": "admin@example.com",
      "fullName": "Admin User",
      "createdAt": "2026-03-02T10:00:00Z",
      "isActive": true
    }
  }
]

--------------------------------
GET /api/v1/activity/cards/{card_id}
--------------------------------
Description:
- Returns recent activity entries for a given card (moves, etc.).

Path params:
- card_id (int)

Response 200 (example):
[
  {
    "id": 10,
    "cardId": 1,
    "type": "move",
    "payload": "from_list=1;to_list=2;to_index=0",
    "createdAt": "2026-03-02T10:05:00Z"
  }
]

--------------------------------
WebSocket: /ws/boards/{board_id}
--------------------------------
URL example:
- ws://127.0.0.1:8000/ws/boards/1

Behavior:
- When a client connects, it starts receiving JSON messages whenever the board is updated (for example, when a card is moved).
- Each message has the same structure as the Board returned by GET /api/v1/boards (single board).

Connection example (pseudo-code):

JS:
const ws = new WebSocket("ws://127.0.0.1:8000/ws/boards/1");

ws.onmessage = (event) => {
  const updatedBoard = JSON.parse(event.data);
  // update UI with updatedBoard
};

