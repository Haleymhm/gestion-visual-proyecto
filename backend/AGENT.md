# Contexto del Proyecto: Gestion Visual de Proyectos

## 1. Descripción del Proyecto

Este proyecto es una aplicación de gestión de tareas inspirada en la metodología **Kanban**, diseñada para ayudar a equipos e individuos a visualizar su flujo de trabajo. Al igual que Trello, permite organizar ideas, tareas y proyectos en tableros dinámicos, ofreciendo una experiencia de usuario fluida e intuitiva.

## 2. Stack Tecnológico

### BACKEND

- **Entorno de Desarrollo:** pip + unicorn.
- **Lenguaje:** Python.
- **Framework:** FastAPI (en la version mas reciente).
- **ORM:** SQLAlchemy 2.0 (estilo declarativo moderno).
- **Base de Datos:** PostgresSQL.
- **Validación:** Pydantic v2.
- **Migraciones:** Alembic.
- **Versionado:** Git.
- **Control de Versiones:** GitHub.
- **Seguridad:** OAuth2 + JWT

#### ESTRUCTURA DEL BACKEND

```
app/
├── core/           # Configuración global, variables de entorno (pydantic-settings)
├── db/             # Sesión de base de datos y Base declarativa
├── models/         # Modelos de SQLAlchemy (Tablas)
├── schemas/        # Modelos de Pydantic (Validación de entrada/salida)
├── crud/           # Lógica de persistencia (Consultas SQL)
├── api/            # Rutas/Endpoints (FastAPI Routers)
└── main.py         # Punto de entrada
```

## 3. Reglas de Codificación

### General

- Usa el idioma ingles
- Prefiere la programación funcional y componentes limpios.
- Documenta las funciones complejas en español.
- No uses variables globales.
- Utiliza versiones para las rutas de la API.

### Backend & Base de Datos

#### Modelos vs Schemas

- **Models (models/):** Representan la base de datos. Usar el estilo Mapped y mapped_column de SQLAlchemy 2.0.

- **Schemas (schemas/):** Representan los datos que viajan por HTTP. Siempre usar Pydantic. Separar en Base, Create y Response (ej. UserCreate, UserPublic).

#### Inyección de Dependencias

Toda interacción con la DB debe usar la dependencia get_db.

Ejemplo: db: ´Session = Depends(get_db)´.

#### Tipado y Documentación

- **Tipado estricto:** Todo parámetro y retorno de función debe tener type hints.
- **Async:** Usar async def para los endpoints, a menos que se use una librería bloqueante que no sea compatible.
- **Status Codes:** Siempre especificar el status_code en el decorador (ej. status_code=status.HTTP_201_CREATED).

#### Manejo de Errores
>
> [!IMPORTANT]
> No retornar diccionarios de error genéricos.

> [!IMPORTANT]
> Lanzar HTTPException de fastapi con el código adecuado (404 para no encontrado, 400 para errores de lógica).

## 4. Convenciones de Nombres

- **Base de Datos:** `camelCase` para campos (ej: `beginDate`), `PascalCase` para modelos (ej: `Ticket`, `Task`).
- **Variables:** `camelCase` (ej: `espaciosDisponibles`).
- **Archivos:** `kebab-case` o seguir la convención del framework.

## 6. 🚀 Características Principales

- Inicio de sesion con email y contraseña. 
- Tableros Dinámicos: Crea múltiples espacios de trabajo para diferentes proyectos.
- Gestion de usuarios y roles (Admin, Owner, Contributor, Viewer).
- Sistema de Listas y Tarjetas: Organiza tus tareas en columnas personalizables (Ej: To do, In progress, Completed).
- Gestión Detallada de Tareas: Añade descripciones, etiquetas de colores, fechas de vencimiento, Comentarios, Archivos adjuntos y checklists a cada tarjeta.
- Historial de interacciones de cada tarjeta.
- Persistencia de Datos: Sincronización en tiempo real para que nunca pierdas tus avances.
