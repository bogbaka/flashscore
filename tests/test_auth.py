from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db
from app.main import app


TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


def setup_test_database():
    Base.metadata.create_all(bind=test_engine)


def teardown_test_database():
    Base.metadata.drop_all(bind=test_engine)


def test_register_user():
    setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["id"] == 1
        assert data["email"] == "user@example.com"

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        teardown_test_database()


def test_register_duplicate_email():
    setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        first_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "password": "password123",
            },
        )

        assert first_response.status_code == 201

        second_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "password": "anotherpassword",
            },
        )

        assert second_response.status_code == 409

        assert second_response.json() == {
            "detail": "Email already registered"
        }

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        teardown_test_database()


def test_login_returns_access_token():
    setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "password": "password123",
            },
        )

        assert register_response.status_code == 201

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "user@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["access_token"]
        assert data["token_type"] == "bearer"

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        teardown_test_database()


def test_login_rejects_wrong_password():
    setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "password": "password123",
            },
        )

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "user@example.com",
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401

        assert response.json() == {
            "detail": "Invalid email or password"
        }

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        teardown_test_database()


def test_login_rejects_unknown_email():
    setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "unknown@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 401

        assert response.json() == {
            "detail": "Invalid email or password"
        }

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        teardown_test_database()


def test_me_returns_authenticated_user():
    setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "password": "password123",
            },
        )

        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "user@example.com",
                "password": "password123",
            },
        )

        token = login_response.json()["access_token"]

        response = client.get(
            "/api/v1/auth/me",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == 1
        assert data["email"] == "user@example.com"

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        teardown_test_database()


def test_me_requires_authentication():
    setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/auth/me"
        )

        assert response.status_code == 401

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        teardown_test_database()


def test_me_rejects_invalid_token():
    setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/auth/me",
            headers={
                "Authorization": "Bearer invalid-token",
            },
        )

        assert response.status_code == 401

        assert response.json() == {
            "detail": "Invalid authentication token"
        }

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        teardown_test_database()


def test_register_rejects_invalid_email():
    setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "password123",
            },
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        teardown_test_database()