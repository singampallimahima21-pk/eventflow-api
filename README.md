# eventflow-api

A backend API for ingesting, validating, processing, and persisting user event data. Built with FastAPI, SQLAlchemy, and JWT authentication, this service exposes endpoints for user login, single record processing, batch processing, and paginated user retrieval.

## Features

- User login endpoint that issues a JWT access token
- Request validation with Pydantic models
- User data processing pipeline with normalization and validation
- SQLite-backed persistence via SQLAlchemy ORM
- Paginated user retrieval with optional filtering, search, and sorting
- Protected user listing endpoint using bearer token authentication

## Tech stack

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- python-jose (JWT)
- SQLite (default local database)

## Quick start

1. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install fastapi uvicorn sqlalchemy python-jose
```

3. Run the app

```powershell
uvicorn app.main:app --reload
```

4. Open the API docs

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API endpoints

### Health check

- `GET /`
- Returns a basic status message.

### Login

- `POST /api/login`
- Returns an access token for bearer authentication.
- Example response:
  ```json
  {
    "access_token": "<token>",
    "token_type": "bearer"
  }
  ```

### Process single user record

- `POST /api/process-data`
- Request body:
  ```json
  {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "age": 30
  }
  ```
- Validates, normalizes, and saves the user record.

### Process batch user records

- `POST /api/process-batch`
- Request body:
  ```json
  {
    "users": [
      {"name": "Jane Doe", "email": "jane@example.com", "age": 30},
      {"name": "John Smith", "email": "john@example.com", "age": 25}
    ]
  }
  ```
- Processes multiple records in a single request.

### Get users

- `GET /api/users`
- Protected endpoint requiring bearer token from `/api/login`
- Supports query parameters:
  - `page`: page number (default `1`)
  - `size`: page size (default `5`, max `50`)
  - `age`: exact age filter
  - `search`: name search term
  - `sort_by`: column to sort by (e.g. `name`, `age`)
  - `order`: `asc` or `desc`

## Project structure

- `app/main.py` — app entrypoint and route registration
- `app/core/auth.py` — JWT creation and token verification
- `app/db/database.py` — SQLAlchemy engine and session setup
- `app/models/user_model.py` — database model for user records
- `app/routes/user_routes.py` — user-related API routes
- `app/schemas/user_schema.py` — request payload validators
- `app/services/user_service.py` — business logic, validation, and database operations

## Notes

- The default database file is `users.db` in the project root.
- `/api/users` is protected by JWT authentication.
- The current login endpoint issues a static dummy user token and can be extended to validate real users.
