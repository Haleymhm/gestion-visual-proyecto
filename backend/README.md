# Kanban Task Manager - Backend

Una aplicación de gestión de tareas inspirada en **Kanban**, diseñada para ayudar a equipos e individuos a visualizar su flujo de trabajo. Similar a Trello, permite organizar ideas, tareas y proyectos en tableros dinámicos.

## Características

- ✅ Autenticación con email y contraseña usando JWT
- ✅ Tableros dinámicos para diferentes proyectos
- ✅ Gestión de usuarios y roles (Admin, Owner, Contributor, Viewer)
- ✅ Listas y tarjetas organizables
- ✅ Tarjetas detalladas con descripción, etiquetas, fechas de vencimiento
- ✅ Comentarios en tarjetas
- ✅ Checklists dentro de tarjetas
- ✅ Historial de interacciones
- ✅ Sincronización en tiempo real (persistencia de datos)

## Stack Tecnológico

- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **Base de Datos**: PostgreSQL
- **Validación**: Pydantic v2
- **Autenticación**: OAuth2 + JWT
- **Migraciones**: Alembic
- **Servidor**: Uvicorn

## Requisitos Previos

- Python 3.10+
- PostgreSQL
- pip

## Instalación

1. **Clonar el repositorio**

```bash
git clone <repository-url>
cd backend
```

2. **Crear entorno virtual**

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**

```bash
cp .env.example .env
# Editar el archivo .env con tus configuraciones
```

## Configuración de la Base de Datos

1. **Crear la base de datos PostgreSQL**

```bash
createdb kanban_db
```

2. **Ejecutar migraciones** (si las hay)

```bash
alembic upgrade head
```

## Ejecución

Inicia el servidor de desarrollo:

```bash
uvicorn main:app --reload
```

La API estará disponible en: `http://localhost:8000`

### Documentación Interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Estructura del Proyecto

```
backend/
├── app/
│   ├── api/              # Routers/Endpoints
│   │   ├── auth.py       # Autenticación
│   │   ├── boards.py     # Tableros
│   │   ├── lists.py      # Listas
│   │   ├── cards.py      # Tarjetas
│   │   ├── comments.py   # Comentarios
│   │   ├── checklists.py # Checklists
│   │   └── tags.py       # Etiquetas
│   ├── core/             # Configuración global
│   │   ├── config.py     # Variables de entorno
│   │   ├── security.py   # Funciones de seguridad
│   │   └── dependencies.py # Dependencias
│   ├── crud/             # Lógica de persistencia
│   ├── db/               # Configuración de BD
│   ├── models/           # Modelos SQLAlchemy
│   └── schemas/          # Modelos Pydantic
├── main.py               # Punto de entrada
├── requirements.txt      # Dependencias
├── .env.example          # Variables de entorno
└── README.md             # Este archivo
```

## API Endpoints

### Autenticación (`/v1/auth`)
- `POST /register` - Registrar nuevo usuario
- `POST /login` - Iniciar sesión
- `GET /me` - Obtener usuario actual

### Tableros (`/v1/boards`)
- `POST /` - Crear tablero
- `GET /my-boards` - Obtener mis tableros
- `GET /{board_id}` - Obtener tablero
- `PUT /{board_id}` - Actualizar tablero
- `DELETE /{board_id}` - Eliminar tablero
- `POST /{board_id}/members` - Añadir miembro
- `GET /{board_id}/members` - Obtener miembros
- `PUT /{board_id}/members/{user_id}` - Actualizar rol

### Listas (`/v1/boards/{board_id}/lists`)
- `POST /` - Crear lista
- `GET /` - Obtener listas
- `GET /{list_id}` - Obtener lista
- `PUT /{list_id}` - Actualizar lista
- `DELETE /{list_id}` - Eliminar lista
- `POST /reorder` - Reordenar listas

### Tarjetas (`/v1/boards/{board_id}/lists/{list_id}/cards`)
- `POST /` - Crear tarjeta
- `GET /` - Obtener tarjetas
- `GET /{card_id}` - Obtener tarjeta
- `PUT /{card_id}` - Actualizar tarjeta
- `DELETE /{card_id}` - Eliminar tarjeta
- `POST /{card_id}/move` - Mover tarjeta
- `POST /reorder` - Reordenar tarjetas

### Comentarios (`/v1/boards/{board_id}/cards/{card_id}/comments`)
- `POST /` - Crear comentario
- `GET /` - Obtener comentarios
- `PUT /{comment_id}` - Actualizar comentario
- `DELETE /{comment_id}` - Eliminar comentario

### Checklists (`/v1/boards/{board_id}/cards/{card_id}/checklists`)
- `POST /` - Crear checklist
- `GET /` - Obtener checklists
- `GET /{checklist_id}` - Obtener checklist
- `PUT /{checklist_id}` - Actualizar checklist
- `DELETE /{checklist_id}` - Eliminar checklist
- `POST /{checklist_id}/items` - Crear item
- `PUT /{checklist_id}/items/{item_id}` - Actualizar item
- `DELETE /{checklist_id}/items/{item_id}` - Eliminar item

### Etiquetas (`/v1/boards/{board_id}/cards/{card_id}/tags`)
- `POST /` - Crear etiqueta
- `GET /` - Obtener etiquetas
- `POST /add-to-card` - Añadir etiqueta a tarjeta
- `DELETE /{tag_id}` - Eliminar etiqueta de tarjeta

## Roles de Usuario

- **Admin**: Control total de la plataforma
- **Owner**: Creador del tablero, control total del tablero
- **Contributor**: Puede crear y editar tarjetas, comentarios y checklists
- **Viewer**: Solo lectura

## Seguridad

- Las contraseñas se hashean con bcrypt
- La autenticación se realiza con JWT
- Las variables sensibles se leen de un archivo `.env`
- Validación de entrada con Pydantic v2
- Inyección de dependencias para seguridad

## Desarrollo

### Crear un User

```bash
curl -X POST "http://localhost:8000/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "username",
    "fullName": "Full Name",
    "password": "secure_password"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password"
  }'
```

## Convenciones de Código

- Usar inglés en el código
- Programación funcional y componentes limpios
- Documentar funciones complejas en español
- Type hints en todo parámetro y retorno
- Status codes siempre especificados
- No usar variables globales
- Usar versiones en las rutas de la API

## Contacto

Para más información o soporte, contactar a [tu correo o información de contacto].

## Licencia

Este proyecto está bajo la licencia MIT.
