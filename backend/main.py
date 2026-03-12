from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.base import Base, engine
from app.api import auth, boards, lists, cards, comments, checklists, tags

# Crear las tablas en la BD
Base.metadata.create_all(bind=engine)

# Crear la aplicación FastAPI
app = FastAPI(
    title="Kanban Task Manager API",
    description="API para gestión de tareas con metodología Kanban",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)
app.include_router(boards.router)
app.include_router(lists.router)
app.include_router(cards.router)
app.include_router(comments.router)
app.include_router(checklists.router)
app.include_router(tags.router)


@app.get("/", tags=["root"])
async def root():
    """Endpoint raíz de la API."""
    return {
        "message": "Bienvenido a la API de Kanban Task Manager",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Verifica el estado de la aplicación."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
