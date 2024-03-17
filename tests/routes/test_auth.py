from unittest.mock import MagicMock

from src.database.models import Users


def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == user.get("email")
    assert "id" in data["user"]


def test_repeat_create_user(client, user):
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Account already exists"


def test_login_user_not_confirmed(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("username"), "password": user.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed"


def test_confirmed_email_error(client):
    response = client.get(
        "/api/auth/confirmed_email/email"
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Verification error"


def test_request_email(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.get(
        "/api/auth/request_email",
        json={"email": user.get("email")},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Check your email for confirmation."


def test_confirmed_email(client, user):
    response = client.get(
        f"/api/auth/confirmed_email/{user.get("email")}"
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Email confirmed"


def test_request_email_is_already_confirmed(client, user, monkeypatch):
    response = client.get(
        "/api/auth/request_email",
        json={"email": user.get("email")},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Your email is already confirmed"


def test_email_is_already_confirmed(client, user):
    response = client.get(
        f"/api/auth/confirmed_email/{user.get("email")}"
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Your email is already confirmed"


def test_login_user(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("username"), "password": user.get("passwor")},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get("username"), "password": "password"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password"


def test_login_wrong_username(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": "username", "password": user.get("password")},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid username"


def test_refresh_token(client, session, user):
    user_odj: Users = session.query(Users).filter(Users.username == user.get("username")).first()
    response = client.get(
        "/api/auth/refresh-token",
        headers={"Authorization": f"Bearer {user_odj.refresh_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"


def test_invalid_refresh_token(client):
    response = client.get(
        "/api/auth/refresh-token",
        headers={"Authorization": f"Bearer {"refresh_token"}"},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid refresh token"
