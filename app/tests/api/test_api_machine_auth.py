from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_good_login():

    response = client.post(url="/api/auth/login",
                           data={"username": "123456789", "password": "password123"})

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_bad_ggv_serial():

    response = client.post(url="/api/auth/login",
                           data={"username": "12345678", "password": "password123"})

    assert response.status_code == 403
    assert "access_token" not in response.json()
    assert "token_type" not in response.json()


def test_bad_password():

    response = client.post(url="/api/auth/login",
                           data={"username": "123456789", "password": "password"})

    assert response.status_code == 403
    assert "access_token" not in response.json()
    assert "token_type" not in response.json()


def test_bad_serial_and_password():

    response = client.post(url="/api/auth/login",
                           data={"username": "12345678", "password": "password"})

    assert response.status_code == 403
    assert "access_token" not in response.json()
    assert "token_type" not in response.json()


def test_unprcessable_entity():

    response = client.post(url="/api/auth/login",
                           data={"username": "123456789"})

    assert response.status_code == 422
