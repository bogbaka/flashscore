from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models.competition import Competition
from app.models.match import Match
from app.models.season import Season
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

    competition = Competition(
        provider_id=5001,
        name="Test Premier League",
        country="England",
        logo_url="https://example.com/competition.png",
    )

    home_team = Team(
        provider_id=5001,
        name="Home United",
        short_name="HOM",
        logo_url="https://example.com/home.png",
    )

    away_team = Team(
        provider_id=5002,
        name="Away City",
        short_name="AWA",
        logo_url="https://example.com/away.png",
    )

    db.add_all(
        [
            competition,
            home_team,
            away_team,
        ]
    )

    db.commit()

    season = Season(
        competition_id=competition.id,
        year=2024,
    )

    db.add(season)
    db.commit()

    db.add_all(
        [
            Match(
                provider_id=6001,
                competition_id=competition.id,
                season_id=season.id,
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                kickoff_at=datetime(
                    2024,
                    8,
                    17,
                    11,
                    30,
                    tzinfo=timezone.utc,
                ),
                status="FT",
                home_score=0,
                away_score=2,
            ),
            Match(
                provider_id=6002,
                competition_id=competition.id,
                season_id=season.id,
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                kickoff_at=datetime(
                    2024,
                    8,
                    18,
                    13,
                    0,
                    tzinfo=timezone.utc,
                ),
                status="FT",
                home_score=2,
                away_score=1,
            ),
            Match(
                provider_id=6003,
                competition_id=competition.id,
                season_id=season.id,
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                kickoff_at=datetime(
                    2024,
                    8,
                    19,
                    15,
                    0,
                    tzinfo=timezone.utc,
                ),
                status="1H",
                home_score=1,
                away_score=0,
            ),
        ]
    )

    db.commit()

    return db


def teardown_test_database():
    Base.metadata.drop_all(bind=test_engine)


def test_get_matches_returns_all_matches():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/matches/"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["page"] == 1
        assert data["limit"] == 20
        assert data["total"] == 3
        assert len(data["matches"]) == 3

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_matches_by_status():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/matches/",
            params={
                "status": "FT",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["total"] == 2
        assert len(data["matches"]) == 2

        assert all(
            match["status"] == "FT"
            for match in data["matches"]
        )

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_matches_live_status():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/matches/",
            params={
                "status": "LIVE",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["total"] == 1
        assert len(data["matches"]) == 1
        assert data["matches"][0]["status"] == "1H"

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_matches_by_date():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/matches/",
            params={
                "date": "2024-08-18",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["total"] == 1
        assert len(data["matches"]) == 1

        match = data["matches"][0]

        assert match["status"] == "FT"
        assert match["home_score"] == 2
        assert match["away_score"] == 1

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_matches_by_different_date_returns_different_match():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        first_response = client.get(
            "/api/v1/matches/",
            params={
                "date": "2024-08-17",
            },
        )

        second_response = client.get(
            "/api/v1/matches/",
            params={
                "date": "2024-08-18",
            },
        )

        assert first_response.status_code == 200
        assert second_response.status_code == 200

        first_match = first_response.json()["matches"][0]
        second_match = second_response.json()["matches"][0]

        assert first_match["home_score"] == 0
        assert first_match["away_score"] == 2

        assert second_match["home_score"] == 2
        assert second_match["away_score"] == 1

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_status_and_date_cannot_be_used_together():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/matches/",
            params={
                "status": "FT",
                "date": "2024-08-18",
            },
        )

        assert response.status_code == 400

        assert response.json() == {
            "detail": "Use either status or date, not both"
        }

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_matches_rejects_invalid_status():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/matches/",
            params={
                "status": "banana",
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


def test_get_matches_supports_pagination():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/matches/",
            params={
                "page": 1,
                "limit": 2,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["page"] == 1
        assert data["limit"] == 2
        assert data["total"] == 3
        assert len(data["matches"]) == 2

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_matches_rejects_invalid_pagination():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/matches/",
            params={
                "page": 0,
            },
        )

        assert response.status_code == 422

        response = client.get(
            "/api/v1/matches/",
            params={
                "limit": 0,
            },
        )

        assert response.status_code == 422

        response = client.get(
            "/api/v1/matches/",
            params={
                "limit": 101,
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