# Quick Start Guide - Kanban Task Manager Backend

## 🚀 Inicio Rápido (5 minutos)

### 1. Preparar el Entorno

```bash
# Navegar al directorio del backend
cd backend

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Iniciar la Base de Datos

```bash
# Usa Docker Compose (recomendado)
docker-compose up -d

# O configura PostgreSQL manualmente y actualiza .env
```

### 3. Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# El contenido por defecto sirve si usas docker-compose
```

### 4. Crear las Tablas en la BD

```bash
# FastAPI creará las tablas automáticamente al iniciar
# Si usas Alembic (migraciones):
alembic upgrade head
```

### 5. Iniciar el Servidor

```bash
# Opción 1: Con uvicorn directamente
uvicorn main:app --reload

# Opción 2: Usando el Makefile
make dev
```

El servidor estará disponible en: **http://localhost:8000**

## 📚 Documentación

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📝 Ejemplo de Uso

### 1. Registrar un usuario

```bash
curl -X POST "http://localhost:8000/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "myuser",
    "fullName": "My User",
    "password": "password123"
  }'
```

### 2. Iniciar sesión

```bash
curl -X POST "http://localhost:8000/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# Respuesta:
# {
#   "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "token_type": "bearer"
# }
```

### 3. Crear un tablero

```bash
curl -X POST "http://localhost:8000/v1/boards" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "title": "Mi Primer Tablero",
    "description": "Descripción del tablero",
    "isPublic": false
  }'
```

### 4. Crear una lista

```bash
curl -X POST "http://localhost:8000/v1/boards/1/lists" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "title": "To Do",
    "position": 0
  }'
```

### 5. Crear una tarjeta

```bash
curl -X POST "http://localhost:8000/v1/boards/1/lists/1/cards" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "title": "Mi Primera Tarea",
    "description": "Descripción de la tarea",
    "color": "#FF5733",
    "dueDate": "2024-12-31T23:59:59"
  }'
```

## 🛠️ Comandos Útiles

```bash
# Ver todos los comandos disponibles
make help

# Parar la BD
docker-compose down

# Ver logs de la BD
docker-compose logs -f db

# Limpiar archivos temporales
make clean

# Crear migración nueva (si usas Alembic)
alembic revision --autogenerate -m "Descripción del cambio"
```

## 📁 Estructura de Carpetas

```
backend/
├── app/
│   ├── api/          # Endpoints
│   ├── core/         # Configuración
│   ├── crud/         # Operaciones de BD
│   ├── db/           # Conexión a BD
│   ├── models/       # Modelos de BD
│   └── schemas/      # Validación de datos
├── main.py           # Entrada de la aplicación
├── requirements.txt  # Dependencias
├── docker-compose.yml # BD con Docker
├── .env.example      # Variables de entorno
└── README.md         # Documentación completa
```

## 🔐 Autenticación

Todos los endpoints (excepto `/auth/register` y `/auth/login`) requieren un token JWT.

Para usar un endpoint protegido:

```bash
Authorization: Bearer <access_token>
```

## ⚙️ Configuración

Las variables importantes se encuentran en `.env`:

```env
DATABASE_URL=postgresql://kanban_user:kanban_password@localhost:5432/kanban_db
SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
```

## 🆘 Solución de Problemas

### La BD no conecta
- Verifica que docker-compose esté corriendo: `docker-compose ps`
- Comprueba la DATABASE_URL en `.env`

### Errores al instalar dependencias
- Asegúrate de estar en el entorno virtual: `source .venv/bin/activate`
- Actualiza pip: `pip install --upgrade pip`

### Puerto 8000 ya está en uso
- Cambia el puerto: `uvicorn main:app --reload --port 8001`

## 📞 Soporte

Para más información, lee el `README.md` completo o consulta la documentación en Swagger (http://localhost:8000/docs)

¡Listo! El backend está funcionando ✨
