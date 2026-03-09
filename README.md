# Gestion Visual de Proyectos (Kanban)

Aplicación de gestión visual de tareas inspirada en Kanban/Trello, con:

- **Tableros dinámicos** con listas y tarjetas.
- **Drag & Drop** con persistencia en base de datos.
- **Usuarios y roles de tablero** (owner/member).
- **Historial de actividad** por tarjeta.
- **Sincronización en tiempo real** vía WebSockets.

## 1. Stack

- **Frontend**: Next.js (app router), TypeScript, TailwindCSS, `@hello-pangea/dnd`.
- **Backend**: FastAPI, SQLAlchemy 2, Pydantic v2, Postgres.

## 2. Requisitos

- Python 3.10+
- Node.js + pnpm
- Postgres en local (por defecto):
  - `postgresql+psycopg2://postgres:postgres@localhost:5432/kanban_db`

Puedes cambiar la URL en `app/core/config.py` o vía variable de entorno `DATABASE_URL`.

## 3. Instalación

```bash
cd gestion-visual-proyecto

# Backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Frontend
cd frontend
pnpm install
```

## 4. Ejecutar la aplicación

En una terminal (backend):

```bash
.venv/bin/python -m uvicorn app.main:app --reload
```

En otra terminal (frontend):

```bash
cd frontend
pnpm dev
```

- API: `http://127.0.0.1:8000`
- Frontend: `http://localhost:3000`

Si quieres usar una URL distinta para la API desde el frontend, crea `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

## 5. Endpoints principales (resumen)

- `GET /api/v1/boards`  
  Lista tableros con listas y tarjetas.

- `POST /api/v1/boards/{board_id}/move-card`  
  Mueve una tarjeta entre listas/posiciones, reordena y emite actualización por WebSocket.

- `GET /api/v1/users/boards/{board_id}/members`  
  Devuelve usuarios y roles asociados al tablero.

- `GET /api/v1/activity/cards/{card_id}`  
  Historial reciente de actividad de una tarjeta.

- WebSocket: `ws://127.0.0.1:8000/ws/boards/{board_id}`  
  Stream de actualizaciones de tablero en tiempo real.
