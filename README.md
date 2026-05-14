# eventflow-api

A production-ready backend API for user authentication and data management. Built with FastAPI, SQLAlchemy, JWT authentication, comprehensive logging, and exception handling.

## Quick Start

1. Create and activate a virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies
```powershell
pip install -r requirements.txt
```

3. Run the server
```powershell
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

---

## Testing

Run all tests with pytest:
```powershell
pytest tests/ -v
```

Tests are located in the root-level `tests/` directory and include:
- User signup tests
- Duplicate email prevention tests
- User login tests
- Database cleanup between tests for reliable, isolated test execution

---

## API Endpoints

### 1. Sign Up

**URL:** `POST http://127.0.0.1:8000/api/signup`

**Request Body:**
```json
{
  "name": "Shivani",
  "email": "shivani@gmail.com",
  "password": "1234"
}
```

**Response (Success):**
```json
{
  "message": "User created successfully",
  "user_id": 1
}
```

**Response (Duplicate Email):**
```json
{
  "status": "error",
  "message": "Email already registered",
  "path": "/api/signup"
}
```

---

### 2. Login

**URL:** `POST http://127.0.0.1:8000/api/login`

**Request Body:**
```json
{
  "email": "shivani@gmail.com",
  "password": "1234"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## Features

- ✅ User signup with password hashing (pbkdf2_sha256)
- ✅ User login with JWT token generation
- ✅ Email validation and duplicate email prevention
- ✅ SQLite database persistence with automatic schema management
- ✅ CSV batch upload and data processing
- ✅ Paginated user retrieval with filtering and sorting
- ✅ Production-style centralized logging with file and console output
- ✅ Global exception handling with consistent error responses
- ✅ Comprehensive request/response logging for debugging
- ✅ Nullable password field for batch processing workflows

## API Documentation

- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

## API Endpoints

### Health Check

- `GET /`
- Returns a basic status message.

### Signup

- `POST /api/signup`
- Request body:
  ```json
  {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "age": 30,
    "password": "securepassword"
  }
  ```
- Creates a new user account with hashed password.
- Returns 400 if email already exists.

### Login

- `POST /api/login`
- Request body:
  ```json
  {
    "email": "jane@example.com",
    "password": "securepassword"
  }
  ```
- Returns an access token for bearer authentication.
- Example response:
  ```json
  {
    "access_token": "<token>",
    "token_type": "bearer"
  }
  ```

### Process Single User Record

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
- Returns error details if email already exists or validation fails.

### Process Batch User Records

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

### Upload CSV

- `POST /api/upload-csv`
- Uploads a CSV file for batch processing.
- CSV should have columns: name, email, age
- Processes each row and saves valid records.

### Get Users

- `GET /api/users`
- Protected endpoint requiring bearer token from `/api/login`
- Supports query parameters:
  - `page`: page number (default `1`)
  - `size`: page size (default `5`, max `50`)
  - `age`: exact age filter
  - `search`: name search term
  - `sort_by`: column to sort by (e.g. `name`, `age`)
  - `order`: `asc` or `desc`

## Project Structure

```
app/
  main.py                 — FastAPI app entry point and route registration
  core/
    auth.py               — JWT token creation and verification
    exceptions.py         — Global exception handlers for consistent error responses
    logger.py             — Centralized logging configuration
    security.py           — Password hashing and verification
  db/
    database.py           — SQLAlchemy engine, session setup, and schema management
  models/
    user_model.py         — SQLAlchemy ORM model for user records
  routes/
    user_routes.py        — User-related API endpoints with comprehensive logging
  schemas/
    user_schema.py        — Pydantic request/response validators
  services/
    user_service.py       — Business logic, validation, and database operations

tests/
  conftest.py             — Pytest fixtures for test client and database cleanup
  test_users.py           — User signup, login, and duplicate email tests
  test_auth.py            — Authentication-related tests (placeholder)

logs/
  app.log                 — Application logs with timestamp, level, module, and line numbers
```

## Logging

The application uses centralized logging configured in `app/core/logger.py`:

- **Log Level:** INFO (captures all INFO, WARNING, ERROR, and CRITICAL messages)
- **Format:** `%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s`
- **Output:** 
  - Console: Colored output for quick debugging
  - File: `logs/app.log` for persistent record-keeping
- **Coverage:** All endpoints, business logic, database operations, and error conditions

Example log entry:
```
2026-05-14 12:25:41,718 - INFO - user_routes.py:205 - [request-id] Incoming request: name='Jane Doe' email='jane@example.com' age=30
```

## Exception Handling

Global exception handlers (`app/core/exceptions.py`) ensure consistent error responses:

- **HTTPException:** Returns status code, message, and request path
- **Generic Exceptions:** Logged with full traceback for debugging
- **Response Format:**
  ```json
  {
    "status": "error",
    "message": "Descriptive error message",
    "path": "/api/endpoint"
  }
  ```

## Database

- **Engine:** SQLite (`users.db`)
- **ORM:** SQLAlchemy
- **Features:**
  - Automatic schema creation on startup
  - Nullable password field for batch processing workflows
  - Duplicate email cleanup on initialization
  - Automatic UNIQUE index on email field

## Notes

- The default database file is `users.db` in the project root.
- `/api/users` is protected by JWT authentication.
- All endpoints include comprehensive logging for production debugging.
- Duplicate email detection prevents data integrity issues.
- Batch processing supports users without passwords for flexible data workflows.
