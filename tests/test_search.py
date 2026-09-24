from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


def setup_test_database():
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()

    db.add_all(
        [
            Team(
                provider_id=7001,
                name="Arsenal",
                short_name="ARS",
                logo_url="https://example.com/arsenal.png",
            ),
            Team(
                provider_id=7002,
                name="Liverpool",
                short_name="LIV",
                logo_url="https://example.com/liverpool.png",
            ),
            Team(
                provider_id=7003,
                name="Manchester City",
                short_name="MCI",
                logo_url="https://example.com/city.png",
            ),
            Competition(
                provider_id=8001,
                name="Premier League",
                country="England",
                logo_url="https://example.com/premier-league.png",
            ),
            Competition(
                provider_id=8002,
                name="La Liga",
                country="Spain",
                logo_url="https://example.com/la-liga.png",
            ),
            Competition(
                provider_id=8003,
                name="Serie A",
                country="Italy",
                logo_url="https://example.com/serie-a.png",
            ),
        ]
    )

    db.commit()

    return db


def teardown_test_database():
    Base.metadata.drop_all(bind=test_engine)


def test_search_by_team_name():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/search/",
            params={
                "q": "Arsenal",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data["teams"]) == 1
        assert data["teams"][0]["name"] == "Arsenal"
        assert data["teams"][0]["short_name"] == "ARS"

        assert data["competitions"] == []

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_search_by_team_short_name():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/search/",
            params={
                "q": "LIV",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data["teams"]) == 1
        assert data["teams"][0]["name"] == "Liverpool"

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_search_by_competition_name():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/search/",
            params={
                "q": "Premier",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["teams"] == []
        assert len(data["competitions"]) == 1
        assert data["competitions"][0]["name"] == "Premier League"

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_search_by_competition_country():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/search/",
            params={
                "q": "Spain",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["teams"] == []
        assert len(data["competitions"]) == 1
        assert data["competitions"][0]["name"] == "La Liga"
        assert data["competitions"][0]["country"] == "Spain"

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_search_is_case_insensitive():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/search/",
            params={
                "q": "aRsEnAl",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data["teams"]) == 1
        assert data["teams"][0]["name"] == "Arsenal"

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_search_returns_empty_results_when_no_match():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/search/",
            params={
                "q": "DoesNotExist",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data == {
            "teams": [],
            "competitions": [],
        }

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_search_validates_query_and_limit():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/search/",
        )

        assert response.status_code == 422

        response = client.get(
            "/api/v1/search/",
            params={
                "q": "",
            },
        )

        assert response.status_code == 422

        response = client.get(
            "/api/v1/search/",
            params={
                "q": "Arsenal",
                "limit": 0,
            },
        )

        assert response.status_code == 422

        response = client.get(
            "/api/v1/search/",
            params={
                "q": "Arsenal",
                "limit": 51,
            },
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_search_rejects_whitespace_only_query():
    setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/search/",
            params={
                "q": "   ",
            },
        )

        assert response.status_code == 422
        assert response.json() == {
            "detail": "Search query cannot be empty"
        }

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        teardown_test_database()