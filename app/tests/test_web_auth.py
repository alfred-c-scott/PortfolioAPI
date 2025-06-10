# app/tests/test_web_auth.py
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.tests import config

client = TestClient(app)


def test_user_exists():
    from app.database import SessionLocal
    from app.models import Staff

    db = SessionLocal()
    user = db.query(Staff).filter(Staff.email == "alfred@gigavend.com").first()
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
                          data={"username": "alfred@gigavend.com", "password": "password123"},
                          follow_redirects=True)
    assert response.status_code == status.HTTP_200_OK
    assert "Dashboard" in response.text
    # Check that we got redirected to dashboard
    assert response.url.path == "/dashboard"


# def test_dashboard_to_staff_navigation():
#     # Login first
#     login_response = client.post("/login", data={"username": "alfred@gigavend.com", "password": "password123"})

#     # Set cookies on the client instead of passing them per request
#     client.cookies = login_response.cookies

#     # Go to dashboard (no cookies parameter needed)
#     dashboard_response = client.get("/dashboard")
#     assert dashboard_response.status_code == status.HTTP_200_OK
#     assert "Manage Staff" in dashboard_response.text

#     # "Click" the link by making a GET request to /staff (no cookies parameter needed)
#     staff_response = client.get("/staff")
#     assert staff_response.status_code == status.HTTP_200_OK
#     assert "Manage Staff Members" in staff_response.text  # Content from staff.html