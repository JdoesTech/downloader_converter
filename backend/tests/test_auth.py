import os
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-unit-tests-only")
os.environ.setdefault("ALGO", "HS256")
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "test")
os.environ.setdefault("DEBUG", "true")

from app.main import app
from app.repository.auth_repo import JWTRepo


@pytest.fixture
def client():
    return TestClient(app)


def test_jwt_round_trip():
    token = JWTRepo(data={"sub": "user-1", "email": "user@example.com", "roles": ["user"]}).generate_token()
    payload = JWTRepo.extract_token(token)
    assert payload["email"] == "user@example.com"
    assert payload["roles"] == ["user"]


def test_reset_token_purpose_validation():
    reset_token = JWTRepo.generate_reset_token("user@example.com")
    email = JWTRepo.verify_reset_token(reset_token)
    assert email == "user@example.com"


@patch("app.services.auth_service.UsersRepository.find_by_email", new_callable=AsyncMock)
@patch("app.services.auth_service.pwd_context.verify", return_value=False)
def test_login_uses_generic_error(mock_verify, mock_find_by_email, client):
    mock_find_by_email.return_value = None
    response = client.post("/auth/login", json={"email": "missing@example.com", "password": "password123"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


@patch("app.services.auth_service.AuthService.forgot_password_service", new_callable=AsyncMock)
def test_forgot_password_returns_generic_message(mock_forgot, client):
    mock_forgot.return_value = None
    response = client.post("/auth/forgot-password", json={"email": "user@example.com"})
    assert response.status_code == 200
    assert "If an account exists" in response.json()["detail"]


def test_protected_route_requires_token(client):
    response = client.post("/users/me")
    assert response.status_code in (401, 403)
