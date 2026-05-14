import time


def test_signup_success(client, clear_db):
    """Test successful user signup"""
    response = client.post(
        "/api/signup",
        json={
            "name": "Shivani",
            "email": f"shivani_test_{int(time.time())}@gmail.com",
            "age": 25,
            "password": "1234"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User created successfully"

    
def test_duplicate_signup(client, clear_db):
    """Test duplicate signup detection"""
    email = f"duplicate_test_{int(time.time())}@gmail.com"
    
    # First signup should succeed
    response1 = client.post(
        "/api/signup",
        json={
            "name": "Shivani",
            "email": email,
            "age": 25,
            "password": "1234"
        }
    )
    assert response1.status_code == 200
    
    # Second signup with same email should fail
    response2 = client.post(
        "/api/signup",
        json={
            "name": "Shivani",
            "email": email,
            "age": 25,
            "password": "1234"
        }
    )
    assert response2.status_code == 400

    
def test_login(client, clear_db):
    """Test user login"""
    email = f"login_test_{int(time.time())}@gmail.com"
    
    # First create a user
    client.post(
        "/api/signup",
        json={
            "name": "Shivani",
            "email": email,
            "age": 25,
            "password": "1234"
        }
    )
    
    # Then try to login
    response = client.post(
        "/api/login",
        json={
            "email": email,
            "password": "1234"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
