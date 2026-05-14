from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_signup_success():

    response = client.post(
        "/api/signup",
        json={
            "name":"Shivani",
            "email":"shivani_test@gmail.com",
            "age":25,
            "password":"1234"
        }
    )

    assert response.status_code == 200

    data=response.json()

    assert data["message"]=="User created successfully"
    
def test_duplicate_signup():

    response=client.post(
        "/api/signup",
        json={
            "name":"Shivani",
            "email":"shivani_test@gmail.com",
            "age":25,
            "password":"1234"
        }
    )

    assert response.status_code==400
    
def test_login():

    response=client.post(
        "/api/login",
        json={
            "email":"shivani_test@gmail.com",
            "password":"1234"
        }
    )

    assert response.status_code==200

    data=response.json()

    assert "access_token" in data
    

client=TestClient(app)


def test_users_requires_auth():

    response=client.get(
        "/api/users"
    )

    assert response.status_code==401
    
def test_users_with_token():

    login=client.post(
        "/api/login",
        json={
            "email":"shivani_test@gmail.com",
            "password":"1234"
        }
    )

    token=login.json()["access_token"]

    response=client.get(
        "/api/users",
        headers={
            "Authorization":
            f"Bearer {token}"
        }
    )

    assert response.status_code==200