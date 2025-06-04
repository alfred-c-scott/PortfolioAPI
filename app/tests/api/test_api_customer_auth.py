from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_phone_and_email_exist():
    pass


def test_phone_exists():
    pass


def test_email_exists():
    pass
