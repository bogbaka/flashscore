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
from app.models.match_event import MatchEvent
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
        provider_id=7001,
        name="Test Premier League",
        country="England",
        logo_url="https://example.com/competition.png",
    )

    home_team = Team(
        provider_id=7002,
        name="Home United",
        short_name="HOM",
        logo_url="https://example.com/home.png",
    )

    away_team = Team(
        provider_id=7003,
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

    match = Match(
        provider_id=7004,
        competition_id=competition.id,
        season_id=season.id,
        home_team_id=home_team.id,
        away_team_id=away_team.id,
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
        away_score=1,
    )

    db.add(match)
    db.commit()

    db.refresh(match)

    db.add_all(
        [
            MatchEvent(
                match_id=match.id,
                minute=23,
                event_type="GOAL",
                player_name="Home Player",
                team_id=home_team.id,
                description="Home United scores",
            ),
            MatchEvent(
                match_id=match.id,
                minute=67,
                event_type="YELLOW_CARD",
                player_name="Away Player",
                team_id=away_team.id,
                description="Yellow card shown",
            ),
        ]
    )

    db.commit()

    return db


def teardown_test_database():
    Base.metadata.drop_all(bind=test_engine)


def test_get_match_details_returns_match():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/matches/1",
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == 1
        assert data["status"] == "FT"
        assert data["home_score"] == 2
        assert data["away_score"] == 1

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_match_details_includes_teams():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/matches/1",
        )

        assert response.status_code == 200

        data = response.json()

        assert data["home_team"]["name"] == "Home United"
        assert data["home_team"]["short_name"] == "HOM"

        assert data["away_team"]["name"] == "Away City"
        assert data["away_team"]["short_name"] == "AWA"

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_match_details_includes_competition():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/matches/1",
        )

        assert response.status_code == 200

        data = response.json()

        assert data["competition"]["name"] == (
            "Test Premier League"
        )
        assert data["competition"]["country"] == "England"

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_match_details_returns_404_for_missing_match():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/matches/999",
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": "Match not found"
        }

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_match_events_returns_events():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/matches/1/events",
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 2

        assert data[0]["minute"] == 23
        assert data[0]["event_type"] == "GOAL"
        assert data[0]["player_name"] == "Home Player"
        assert data[0]["team_id"] == 1
        assert data[0]["description"] == (
            "Home United scores"
        )

        assert data[1]["minute"] == 67
        assert data[1]["event_type"] == "YELLOW_CARD"
        assert data[1]["player_name"] == "Away Player"
        assert data[1]["team_id"] == 2
        assert data[1]["description"] == (
            "Yellow card shown"
        )

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_match_events_returns_404_for_missing_match():
    db = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/matches/999/events",
        )

        assert response.status_code == 404

        assert response.json() == {
            "detail": "Match not found"
        }

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()