# app/tests/test_web_auth.py
import time
from datetime import datetime, timedelta
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.tests.config import username
from app.tests.config import password

client = TestClient(app)


def test_user_exists():
    from app.database import SessionLocal
    from app.models import Staff

    db = SessionLocal()
    user = db.query(Staff).filter(Staff.email == username).first()
    print(f"User found: {user is not None}")
    if user:
        print(f"User details: {user.email}, {user.username}")
    db.close()
    assert user is not None


def test_login_path():
    response = client.get("/login")
    assert response.status_code == status.HTTP_200_OK


def test_login_success():
    response = client.post("/login",
                          data={"username": username, "password": password},
                          follow_redirects=True)

    assert response.status_code == status.HTTP_200_OK
    assert "Dashboard" in response.text
    # Check that we got redirected to dashboard
    assert response.url.path == "/dashboard"


def test_bad_password():
    response = client.post("/login",
                          data={"username": username, "password": "wrong_password"},
                          follow_redirects=True)

    assert response.status_code == status.HTTP_200_OK
    assert "Invalid credentials" in response.text


def test_bad_username():
    response = client.post("/login",
                          data={"username": "wrong_username", "password": password},
                          follow_redirects=True)

    assert response.status_code == status.HTTP_200_OK
    assert "Invalid credentials" in response.text


def test_bad_username_bad_password():
    response = client.post("/login",
                          data={"username": "wrong_username", "password": "wrong_password"},
                          follow_redirects=True)

    assert response.status_code == status.HTTP_200_OK
    assert "Invalid credentials" in response.text