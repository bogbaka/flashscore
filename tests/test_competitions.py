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
from app.models.standing import Standing
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

    premier_league = Competition(
        provider_id=10001,
        name="Premier League",
        country="England",
        logo_url="https://example.com/premier-league.png",
    )

    la_liga = Competition(
        provider_id=10002,
        name="La Liga",
        country="Spain",
        logo_url="https://example.com/la-liga.png",
    )

    season = Season(
        competition=premier_league,
        year=2024,
    )

    arsenal = Team(
        provider_id=10003,
        name="Arsenal",
        short_name="ARS",
        logo_url="https://example.com/arsenal.png",
    )

    liverpool = Team(
        provider_id=10004,
        name="Liverpool",
        short_name="LIV",
        logo_url="https://example.com/liverpool.png",
    )

    chelsea = Team(
        provider_id=10005,
        name="Chelsea",
        short_name="CHE",
        logo_url="https://example.com/chelsea.png",
    )

    unused_team = Team(
        provider_id=10006,
        name="Unused FC",
        short_name="UNU",
        logo_url="https://example.com/unused.png",
    )

    db.add_all(
        [
            premier_league,
            la_liga,
            season,
            arsenal,
            liverpool,
            chelsea,
            unused_team,
        ]
    )

    db.commit()

    standings = [
        Standing(
            competition_id=premier_league.id,
            season_id=season.id,
            team_id=arsenal.id,
            position=1,
            played=2,
            wins=2,
            draws=0,
            losses=0,
            goals_for=5,
            goals_against=1,
            points=6,
        ),
        Standing(
            competition_id=premier_league.id,
            season_id=season.id,
            team_id=liverpool.id,
            position=2,
            played=2,
            wins=1,
            draws=1,
            losses=0,
            goals_for=4,
            goals_against=2,
            points=4,
        ),
        Standing(
            competition_id=premier_league.id,
            season_id=season.id,
            team_id=chelsea.id,
            position=3,
            played=2,
            wins=1,
            draws=0,
            losses=1,
            goals_for=3,
            goals_against=3,
            points=3,
        ),
    ]

    db.add_all(standings)
    db.commit()

    db.add_all(
        [
            Match(
                provider_id=10101,
                competition_id=premier_league.id,
                season_id=season.id,
                home_team_id=arsenal.id,
                away_team_id=liverpool.id,
                kickoff_at=datetime(
                    2024,
                    8,
                    17,
                    15,
                    0,
                    tzinfo=timezone.utc,
                ),
                status="FT",
                home_score=2,
                away_score=0,
            ),
            Match(
                provider_id=10102,
                competition_id=premier_league.id,
                season_id=season.id,
                home_team_id=chelsea.id,
                away_team_id=arsenal.id,
                kickoff_at=datetime(
                    2024,
                    8,
                    18,
                    15,
                    0,
                    tzinfo=timezone.utc,
                ),
                status="FT",
                home_score=1,
                away_score=1,
            ),
            Match(
                provider_id=10103,
                competition_id=premier_league.id,
                season_id=season.id,
                home_team_id=liverpool.id,
                away_team_id=chelsea.id,
                kickoff_at=datetime(
                    2024,
                    8,
                    19,
                    15,
                    0,
                    tzinfo=timezone.utc,
                ),
                status="FT",
                home_score=3,
                away_score=1,
            ),
        ]
    )

    db.commit()

    return db


def teardown_test_database():
    Base.metadata.drop_all(bind=test_engine)


def test_get_competitions_returns_paginated_competitions():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/competitions/",
            params={
                "page": 1,
                "limit": 1,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["page"] == 1
        assert data["limit"] == 1
        assert data["total"] == 2
        assert len(data["competitions"]) == 1

        assert data["competitions"][0]["name"] == "La Liga"

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_competition_details():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/competitions/1",
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == 1
        assert data["name"] == "Premier League"
        assert data["country"] == "England"
        assert data["logo_url"] == (
            "https://example.com/premier-league.png"
        )

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_competition_returns_404_for_missing_competition():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/competitions/999",
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": "Competition not found"
        }

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_competition_matches():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/competitions/1/matches",
        )

        assert response.status_code == 200

        data = response.json()

        assert data["page"] == 1
        assert data["limit"] == 20
        assert data["total"] == 3
        assert len(data["matches"]) == 3

        assert all(
            match["competition"]["name"]
            == "Premier League"
            for match in data["matches"]
        )

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_competition_matches_supports_pagination():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/competitions/1/matches",
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


def test_get_competition_matches_returns_empty_for_competition_without_matches():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/competitions/2/matches",
        )

        assert response.status_code == 200

        data = response.json()

        assert data["total"] == 0
        assert data["matches"] == []

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_competition_matches_returns_404_for_missing_competition():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/competitions/999/matches",
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": "Competition not found"
        }

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_competition_standings():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/competitions/1/standings",
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 3

        assert data[0]["position"] == 1
        assert data[0]["team"]["name"] == "Arsenal"
        assert data[0]["points"] == 6

        assert data[1]["position"] == 2
        assert data[1]["team"]["name"] == "Liverpool"

        assert data[2]["position"] == 3
        assert data[2]["team"]["name"] == "Chelsea"

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_competition_standings_returns_404_when_missing():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/competitions/2/standings",
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": "Standings not found"
        }

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_competition_standings_returns_404_for_missing_competition():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/competitions/999/standings",
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": "Competition not found"
        }

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_competitions_rejects_invalid_pagination():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/competitions/",
            params={
                "page": 0,
            },
        )

        assert response.status_code == 422

        response = client.get(
            "/api/v1/competitions/",
            params={
                "limit": 0,
            },
        )

        assert response.status_code == 422

        response = client.get(
            "/api/v1/competitions/",
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


def test_get_competition_matches_has_deterministic_order():
    setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/competitions/1/matches",
            params={
                "page": 1,
                "limit": 20,
            },
        )

        assert response.status_code == 200

        data = response.json()

        matches = data["matches"]

        for first, second in zip(
            matches,
            matches[1:],
        ):
            first_key = (
                first["kickoff_at"],
                first["id"],
            )

            second_key = (
                second["kickoff_at"],
                second["id"],
            )

            assert first_key <= second_key

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        teardown_test_database()