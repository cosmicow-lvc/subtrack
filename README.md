# Subtrack

Subtrack es una API REST desarrollada con FastAPI para gestionar suscripciones y cargos recurrentes de un usuario. El proyecto permite registrar usuarios, autenticarse con JWT, crear y consultar suscripciones, así como registrar y consultar cargos asociados a cada suscripción.

La aplicación incluye data de demo para arrancar rápidamente en entorno local y está preparada para ejecutarse con PostgreSQL en contenedores.

## Características

- Autenticación con JWT
- Registro e inicio de sesión de usuarios
- CRUD de suscripciones
- Registro de cargos por suscripción
- Validación con Pydantic
- Base de datos PostgreSQL async con SQLAlchemy
- Seed automático en entorno local
- Documentación interactiva de la API con Swagger UI y Redoc

## Stack tecnológico

- Python 3.11+
- FastAPI
- SQLAlchemy 2
- PostgreSQL
- asyncpg
- Pydantic + pydantic-settings
- JWT (PyJWT)
- bcrypt
- pytest + pytest-asyncio
- Docker / Docker Compose

## Requisitos

- Docker y Docker Compose
- Python 3.11+
- PostgreSQL (si se ejecuta localmente sin Docker)

## Variables de entorno

Crea un archivo `.env` en la raíz con esta configuración base:

```env
PROJECT_NAME=Subtrack
ENVIRONMENT=local
DEBUG=false
API_PREFIX=/api

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=subtrack

SECRET_KEY=cualquier_cosa
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
LOG_LEVEL=INFO
```

## Ejecución con Docker

Desde la raíz del proyecto:

```bash
docker compose up --build
```

La API estará disponible en:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc
- Healthcheck: http://localhost:8000/health

## Demo local

Cuando `ENVIRONMENT=local`, la aplicación crea automáticamente una cuenta de demostración si no existe.

- Email: `demo@subtrack.local`
- Contraseña: `Demo1234!`

La demo incluye:

- 3 suscripciones mensuales
- 3 meses de cargos asociados

El seed no se ejecuta en `staging` ni `production` y no duplica la data si la cuenta ya existe.

## Endpoints principales

### Usuarios

```http
POST /api/users/register
POST /api/users/login
GET /api/users/me
```

### Suscripciones

```http
POST /api/subs
GET /api/subs
GET /api/subs/{sub_id}
PUT /api/subs/{sub_id}
DELETE /api/subs/{sub_id}
```

### Cargos

```http
POST /api/charges
GET /api/charges
GET /api/charges/{charge_id}
DELETE /api/charges/{charge_id}
```

### Salud

```http
GET /health
```

## Autenticación

La API protege los endpoints de suscripciones y cargos con JWT. El flujo típico es:

1. Registrarse con `POST /api/users/register`
2. Iniciar sesión con `POST /api/users/login`
3. Usar el token recibido en el header:

```http
Authorization: Bearer <token>
```

## Ejemplo de uso

### Registro

```bash
curl -X POST "http://localhost:8000/api/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "name": "Usuario Ejemplo",
    "password": "MiPassword123!"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@subtrack.local",
    "password": "Demo1234!"
  }'
```

### Listar suscripciones

```bash
curl -X GET "http://localhost:8000/api/subs" \
  -H "Authorization: Bearer <token>"
```

## Pruebas

Ejecuta la suite de pruebas con:

```bash
pytest
```

El proyecto incluye tests para:

- salud de la API
- autenticación de usuarios
- gestión de suscripciones
- gestión de cargos
- seed local
