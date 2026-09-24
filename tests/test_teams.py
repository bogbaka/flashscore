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

    competition = Competition(
        provider_id=9001,
        name="Test Premier League",
        country="England",
        logo_url="https://example.com/competition.png",
    )

    season = Season(
        competition=competition,
        year=2024,
    )

    arsenal = Team(
        provider_id=9002,
        name="Arsenal",
        short_name="ARS",
        logo_url="https://example.com/arsenal.png",
    )

    liverpool = Team(
        provider_id=9003,
        name="Liverpool",
        short_name="LIV",
        logo_url="https://example.com/liverpool.png",
    )

    chelsea = Team(
        provider_id=9004,
        name="Chelsea",
        short_name="CHE",
        logo_url="https://example.com/chelsea.png",
    )

    unused_team = Team(
        provider_id=9005,
        name="Unused FC",
        short_name="UNU",
        logo_url="https://example.com/unused.png",
    )

    db.add_all(
        [
            competition,
            season,
            arsenal,
            liverpool,
            chelsea,
            unused_team,
        ]
    )

    db.commit()

    standing = Standing(
        competition_id=competition.id,
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
    )

    db.add(standing)
    db.commit()

    db.add_all(
        [
            Match(
                provider_id=9010,
                competition_id=competition.id,
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
                provider_id=9011,
                competition_id=competition.id,
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
                provider_id=9012,
                competition_id=competition.id,
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


def test_get_teams_returns_paginated_teams():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/teams/",
            params={
                "page": 1,
                "limit": 2,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["page"] == 1
        assert data["limit"] == 2
        assert data["total"] == 4
        assert len(data["teams"]) == 2

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_team_details_includes_standing():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/teams/1",
            params={
                "competition_id": 1,
                "season_id": 1,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["name"] == "Arsenal"
        assert data["short_name"] == "ARS"
        assert data["logo_url"] == (
            "https://example.com/arsenal.png"
        )

        assert data["standing"] is not None
        assert data["standing"]["position"] == 1
        assert data["standing"]["played"] == 2
        assert data["standing"]["wins"] == 2
        assert data["standing"]["points"] == 6

        assert data["standing"]["team"]["name"] == "Arsenal"

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_team_details_without_standing_context():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/teams/1",
        )

        assert response.status_code == 200

        data = response.json()

        assert data["name"] == "Arsenal"
        assert data["standing"] is None

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_team_details_without_standing():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/teams/2",
        )

        assert response.status_code == 200

        data = response.json()

        assert data["name"] == "Liverpool"
        assert data["standing"] is None

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_team_returns_404_for_missing_team():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/teams/999",
        )

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Team not found"
        }

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_team_requires_both_standing_context_parameters():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/teams/1",
            params={
                "competition_id": 1,
            },
        )

        assert response.status_code == 400

        assert response.json() == {
            "detail": (
                "competition_id and season_id "
                "must be provided together"
            )
        }

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_team_does_not_return_standing_from_wrong_competition():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/teams/1",
            params={
                "competition_id": 999,
                "season_id": 999,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["standing"] is None

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_team_matches_returns_only_team_matches():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/teams/1/matches",
        )

        assert response.status_code == 200

        data = response.json()

        assert data["total"] == 2
        assert len(data["matches"]) == 2

        assert all(
            match["home_team"]["name"] == "Arsenal"
            or match["away_team"]["name"] == "Arsenal"
            for match in data["matches"]
        )

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_team_matches_supports_pagination():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/teams/1/matches",
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
        assert len(data["matches"]) == 1

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_team_matches_returns_empty_for_team_without_matches():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/teams/4/matches",
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


def test_get_team_matches_rejects_invalid_pagination():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/teams/1/matches",
            params={
                "page": 0,
            },
        )

        assert response.status_code == 422

        response = client.get(
            "/api/v1/teams/1/matches",
            params={
                "limit": 0,
            },
        )

        assert response.status_code == 422

        response = client.get(
            "/api/v1/teams/1/matches",
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


def test_get_team_matches_orders_by_kickoff_and_id():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/teams/1/matches",
            params={
                "page": 1,
                "limit": 20,
            },
        )

        assert response.status_code == 200

        data = response.json()

        match_ids = [
            match["id"]
            for match in data["matches"]
        ]

        assert match_ids == sorted(
            match_ids,
            key=lambda match_id: (
                next(
                    match["kickoff_at"]
                    for match in data["matches"]
                    if match["id"] == match_id
                ),
                match_id,
            ),
        )

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        teardown_test_database()