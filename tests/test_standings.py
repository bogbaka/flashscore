from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models.competition import Competition
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
        provider_id=9991,
        name="Test Premier League",
        country="England",
        logo_url="https://example.com/competition.png",
    )

    team = Team(
        provider_id=9991,
        name="Test United",
        short_name="TST",
        logo_url="https://example.com/team.png",
    )

    db.add_all(
        [
            competition,
            team,
        ]
    )

    db.commit()

    season = Season(
        competition_id=competition.id,
        year=2024,
    )

    db.add(season)
    db.commit()

    standing = Standing(
        competition_id=competition.id,
        season_id=season.id,
        team_id=team.id,
        position=1,
        played=10,
        wins=8,
        draws=1,
        losses=1,
        goals_for=20,
        goals_against=5,
        points=25,
    )

    db.add(standing)
    db.commit()

    return (
        db,
        competition,
        team,
        season,
        standing,
    )


def teardown_test_database():
    Base.metadata.drop_all(bind=test_engine)


def test_standings_require_competition_id():
    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/standings/"
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )


def test_get_competition_standings():
    (
        db,
        competition,
        team,
        season,
        standing,
    ) = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/standings/",
            params={
                "competition_id": competition.id,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1
        assert data[0]["competition_id"] == competition.id
        assert data[0]["season_id"] == season.id
        assert data[0]["team_id"] == team.id
        assert data[0]["position"] == 1
        assert data[0]["played"] == 10
        assert data[0]["wins"] == 8
        assert data[0]["draws"] == 1
        assert data[0]["losses"] == 1
        assert data[0]["goals_for"] == 20
        assert data[0]["goals_against"] == 5
        assert data[0]["points"] == 25
        assert data[0]["team"]["name"] == "Test United"

    finally:
        app.dependency_overrides.pop(
            get_db,
            None,
        )

        db.close()
        teardown_test_database()


def test_get_competition_standings_returns_404_when_missing():
    db, *_ = setup_test_database()

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            "/api/v1/standings/competition/999999"
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