from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.models.competition import Competition
from app.models.match import Match
from app.models.season import Season
from app.models.team import Team
from app.repositories.match import MatchRepository


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


def setup_test_database():
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()

    home_team = Team(
        provider_id=1001,
        name="Home United",
        short_name="HOM",
        logo_url="https://example.com/home.png",
    )

    away_team = Team(
        provider_id=1002,
        name="Away City",
        short_name="AWA",
        logo_url="https://example.com/away.png",
    )

    competition = Competition(
        provider_id=2001,
        name="Test Premier League",
        country="England",
        logo_url="https://example.com/competition.png",
    )

    db.add_all(
        [
            home_team,
            away_team,
            competition,
        ]
    )

    db.commit()

    season = Season(
        competition_id=competition.id,
        year=2024,
    )

    db.add(season)
    db.commit()

    return db, home_team, away_team, competition, season


def teardown_test_database():
    Base.metadata.drop_all(bind=test_engine)


def test_live_matches_include_all_supported_live_statuses():
    (
        db,
        home_team,
        away_team,
        competition,
        season,
    ) = setup_test_database()

    try:
        live_statuses = [
            "1H",
            "HT",
            "2H",
            "ET",
            "BT",
            "P",
            "LIVE",
        ]

        matches = []

        for index, status in enumerate(
            live_statuses,
            start=1,
        ):
            matches.append(
                Match(
                    provider_id=index,
                    competition_id=competition.id,
                    season_id=season.id,
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    kickoff_at=datetime(
                        2024,
                        8,
                        17,
                        10 + index,
                        0,
                        tzinfo=timezone.utc,
                    ),
                    status=status,
                    home_score=1,
                    away_score=0,
                )
            )

        db.add_all(matches)
        db.commit()

        repository = MatchRepository(db)

        live_matches, total = repository.get_live(
            page=1,
            limit=20,
        )

        returned_statuses = {
            match.status
            for match in live_matches
        }

        assert total == len(live_statuses)
        assert returned_statuses == set(live_statuses)

    finally:
        db.close()
        teardown_test_database()