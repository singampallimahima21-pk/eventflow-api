import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from app.main import app
from app.db.database import SessionLocal, engine
from app.models.user_model import User


@pytest.fixture(scope="function")
def client():
    """Test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture(scope="function")
def clear_db():
    """Clear users table before each test"""
    db = SessionLocal()
    try:
        # Delete all users
        db.query(User).delete()
        db.commit()
    finally:
        db.close()
    
    yield
    
    # Cleanup after test
    db = SessionLocal()
    try:
        db.query(User).delete()
        db.commit()
    finally:
        db.close()
