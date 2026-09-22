from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models.competition import Competition
from app.models.team import Team


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


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)

    app.dependency_overrides[get_db] = override_get_db

    db = TestingSessionLocal()

    team = Team(
        provider_id=1001,
        name="Test United",
        short_name="Test Utd",
        logo_url="https://example.com/team.png",
    )

    competition = Competition(
        provider_id=2001,
        name="Test Premier League",
        country="England",
        logo_url="https://example.com/competition.png",
    )

    db.add_all(
        [
            team,
            competition,
        ]
    )

    db.commit()
    db.close()

    yield

    app.dependency_overrides.clear()

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    return TestClient(app)


def register_and_login(client: TestClient) -> str:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "favorites@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "favorites@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


def test_add_team_favorite(client: TestClient):
    token = register_and_login(client)

    response = client.post(
        "/api/v1/favorites/team/1",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["team_id"] == 1
    assert data["competition_id"] is None
    assert data["team"]["name"] == "Test United"
    assert data["team"]["short_name"] == "Test Utd"


def test_add_competition_favorite(client: TestClient):
    token = register_and_login(client)

    response = client.post(
        "/api/v1/favorites/competition/1",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["competition_id"] == 1
    assert data["team_id"] is None
    assert data["competition"]["name"] == "Test Premier League"


def test_list_favorites_returns_related_data(client: TestClient):
    token = register_and_login(client)

    headers = {
        "Authorization": f"Bearer {token}",
    }

    team_response = client.post(
        "/api/v1/favorites/team/1",
        headers=headers,
    )

    competition_response = client.post(
        "/api/v1/favorites/competition/1",
        headers=headers,
    )

    assert team_response.status_code == 201
    assert competition_response.status_code == 201

    response = client.get(
        "/api/v1/favorites/",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    team_favorite = next(
        favorite
        for favorite in data
        if favorite["team_id"] == 1
    )

    competition_favorite = next(
        favorite
        for favorite in data
        if favorite["competition_id"] == 1
    )

    assert team_favorite["team"]["name"] == "Test United"

    assert (
        competition_favorite["competition"]["name"]
        == "Test Premier League"
    )


def test_duplicate_team_favorite_is_rejected(client: TestClient):
    token = register_and_login(client)

    headers = {
        "Authorization": f"Bearer {token}",
    }

    first_response = client.post(
        "/api/v1/favorites/team/1",
        headers=headers,
    )

    second_response = client.post(
        "/api/v1/favorites/team/1",
        headers=headers,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_duplicate_competition_favorite_is_rejected(
    client: TestClient,
):
    token = register_and_login(client)

    headers = {
        "Authorization": f"Bearer {token}",
    }

    first_response = client.post(
        "/api/v1/favorites/competition/1",
        headers=headers,
    )

    second_response = client.post(
        "/api/v1/favorites/competition/1",
        headers=headers,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_remove_team_favorite(client: TestClient):
    token = register_and_login(client)

    headers = {
        "Authorization": f"Bearer {token}",
    }

    add_response = client.post(
        "/api/v1/favorites/team/1",
        headers=headers,
    )

    assert add_response.status_code == 201

    delete_response = client.delete(
        "/api/v1/favorites/team/1",
        headers=headers,
    )

    assert delete_response.status_code == 204

    list_response = client.get(
        "/api/v1/favorites/",
        headers=headers,
    )

    assert list_response.status_code == 200
    assert list_response.json() == []


def test_remove_competition_favorite(client: TestClient):
    token = register_and_login(client)

    headers = {
        "Authorization": f"Bearer {token}",
    }

    add_response = client.post(
        "/api/v1/favorites/competition/1",
        headers=headers,
    )

    assert add_response.status_code == 201

    delete_response = client.delete(
        "/api/v1/favorites/competition/1",
        headers=headers,
    )

    assert delete_response.status_code == 204

    list_response = client.get(
        "/api/v1/favorites/",
        headers=headers,
    )

    assert list_response.status_code == 200
    assert list_response.json() == []


def test_favorites_require_authentication(client: TestClient):
    response = client.get("/api/v1/favorites/")

    assert response.status_code == 401