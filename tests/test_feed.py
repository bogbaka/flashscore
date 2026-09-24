from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.models.competition import Competition
from app.models.match import Match
from app.models.season import Season
from app.models.team import Team
from app.repositories.feed import FeedRepository


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


def create_match(
    db,
    home_team,
    away_team,
    competition,
    season,
    provider_id: int,
    kickoff_at: datetime,
    status: str,
    home_score: int | None = None,
    away_score: int | None = None,
):
    match = Match(
        provider_id=provider_id,
        competition_id=competition.id,
        season_id=season.id,
        home_team_id=home_team.id,
        away_team_id=away_team.id,
        kickoff_at=kickoff_at,
        status=status,
        home_score=home_score,
        away_score=away_score,
    )

    db.add(match)

    return match


def test_finished_matches_respect_selected_date():
    (
        db,
        home_team,
        away_team,
        competition,
        season,
    ) = setup_test_database()

    try:
        create_match(
            db=db,
            home_team=home_team,
            away_team=away_team,
            competition=competition,
            season=season,
            provider_id=1,
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
        )

        create_match(
            db=db,
            home_team=home_team,
            away_team=away_team,
            competition=competition,
            season=season,
            provider_id=2,
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
        )

        db.commit()

        repository = FeedRepository(db)

        august_17_start = datetime(
            2024,
            8,
            17,
            tzinfo=timezone.utc,
        )

        august_17_end = datetime(
            2024,
            8,
            18,
            tzinfo=timezone.utc,
        )

        august_18_start = august_17_end

        august_18_end = datetime(
            2024,
            8,
            19,
            tzinfo=timezone.utc,
        )

        august_17_matches = repository.get_finished_matches(
            start=august_17_start,
            end=august_17_end,
        )

        august_18_matches = repository.get_finished_matches(
            start=august_18_start,
            end=august_18_end,
        )

        assert len(august_17_matches) == 1
        assert august_17_matches[0].provider_id == 1

        assert len(august_18_matches) == 1
        assert august_18_matches[0].provider_id == 2

    finally:
        db.close()
        teardown_test_database()


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

        start = datetime(
            2024,
            8,
            17,
            tzinfo=timezone.utc,
        )

        for index, status in enumerate(live_statuses, start=1):
            create_match(
                db=db,
                home_team=home_team,
                away_team=away_team,
                competition=competition,
                season=season,
                provider_id=index,
                kickoff_at=start + timedelta(
                    minutes=index
                ),
                status=status,
            )

        db.commit()

        repository = FeedRepository(db)

        matches = repository.get_live_matches(
            start=start,
            end=start + timedelta(days=1),
        )

        returned_statuses = {
            match.status
            for match in matches
        }

        assert returned_statuses == set(
            live_statuses
        )

    finally:
        db.close()
        teardown_test_database()


def test_live_matches_respect_selected_date():
    (
        db,
        home_team,
        away_team,
        competition,
        season,
    ) = setup_test_database()

    try:
        create_match(
            db=db,
            home_team=home_team,
            away_team=away_team,
            competition=competition,
            season=season,
            provider_id=1,
            kickoff_at=datetime(
                2024,
                8,
                17,
                15,
                tzinfo=timezone.utc,
            ),
            status="LIVE",
        )

        create_match(
            db=db,
            home_team=home_team,
            away_team=away_team,
            competition=competition,
            season=season,
            provider_id=2,
            kickoff_at=datetime(
                2024,
                8,
                18,
                15,
                tzinfo=timezone.utc,
            ),
            status="LIVE",
        )

        db.commit()

        repository = FeedRepository(db)

        matches = repository.get_live_matches(
            start=datetime(
                2024,
                8,
                17,
                tzinfo=timezone.utc,
            ),
            end=datetime(
                2024,
                8,
                18,
                tzinfo=timezone.utc,
            ),
        )

        assert len(matches) == 1
        assert matches[0].provider_id == 1

    finally:
        db.close()
        teardown_test_database()


def test_finished_matches_include_all_finished_statuses():
    (
        db,
        home_team,
        away_team,
        competition,
        season,
    ) = setup_test_database()

    try:
        finished_statuses = [
            "FT",
            "AET",
            "PEN",
        ]

        start = datetime(
            2024,
            8,
            17,
            tzinfo=timezone.utc,
        )

        for index, status in enumerate(
            finished_statuses,
            start=1,
        ):
            create_match(
                db=db,
                home_team=home_team,
                away_team=away_team,
                competition=competition,
                season=season,
                provider_id=index,
                kickoff_at=start + timedelta(
                    minutes=index
                ),
                status=status,
                home_score=1,
                away_score=0,
            )

        db.commit()

        repository = FeedRepository(db)

        matches = repository.get_finished_matches(
            start=start,
            end=start + timedelta(days=1),
        )

        returned_statuses = {
            match.status
            for match in matches
        }

        assert returned_statuses == set(
            finished_statuses
        )

    finally:
        db.close()
        teardown_test_database()


def test_finished_matches_are_returned_newest_first():
    (
        db,
        home_team,
        away_team,
        competition,
        season,
    ) = setup_test_database()

    try:
        start = datetime(
            2024,
            8,
            17,
            tzinfo=timezone.utc,
        )

        create_match(
            db=db,
            home_team=home_team,
            away_team=away_team,
            competition=competition,
            season=season,
            provider_id=1,
            kickoff_at=start + timedelta(hours=1),
            status="FT",
        )

        create_match(
            db=db,
            home_team=home_team,
            away_team=away_team,
            competition=competition,
            season=season,
            provider_id=2,
            kickoff_at=start + timedelta(hours=3),
            status="FT",
        )

        create_match(
            db=db,
            home_team=home_team,
            away_team=away_team,
            competition=competition,
            season=season,
            provider_id=3,
            kickoff_at=start + timedelta(hours=2),
            status="FT",
        )

        db.commit()

        repository = FeedRepository(db)

        matches = repository.get_finished_matches(
            start=start,
            end=start + timedelta(days=1),
        )

        assert [
            match.provider_id
            for match in matches
        ] == [2, 3, 1]

    finally:
        db.close()
        teardown_test_database()


def test_finished_matches_respect_limit():
    (
        db,
        home_team,
        away_team,
        competition,
        season,
    ) = setup_test_database()

    try:
        start = datetime(
            2024,
            8,
            17,
            tzinfo=timezone.utc,
        )

        for provider_id in range(1, 6):
            create_match(
                db=db,
                home_team=home_team,
                away_team=away_team,
                competition=competition,
                season=season,
                provider_id=provider_id,
                kickoff_at=start + timedelta(
                    hours=provider_id
                ),
                status="FT",
            )

        db.commit()

        repository = FeedRepository(db)

        matches = repository.get_finished_matches(
            start=start,
            end=start + timedelta(days=1),
            limit=2,
        )

        assert len(matches) == 2

        assert [
            match.provider_id
            for match in matches
        ] == [5, 4]

    finally:
        db.close()
        teardown_test_database()


def test_upcoming_matches_exclude_finished_matches():
    (
        db,
        home_team,
        away_team,
        competition,
        season,
    ) = setup_test_database()

    try:
        now = datetime(
            2024,
            8,
            17,
            12,
            tzinfo=timezone.utc,
        )

        create_match(
            db=db,
            home_team=home_team,
            away_team=away_team,
            competition=competition,
            season=season,
            provider_id=1,
            kickoff_at=now + timedelta(hours=1),
            status="NS",
        )

        create_match(
            db=db,
            home_team=home_team,
            away_team=away_team,
            competition=competition,
            season=season,
            provider_id=2,
            kickoff_at=now + timedelta(hours=2),
            status="FT",
            home_score=1,
            away_score=0,
        )

        db.commit()

        repository = FeedRepository(db)

        matches = repository.get_upcoming_matches(
            now=now,
        )

        assert len(matches) == 1
        assert matches[0].provider_id == 1

    finally:
        db.close()
        teardown_test_database()


def test_upcoming_matches_are_ordered_by_kickoff():
    (
        db,
        home_team,
        away_team,
        competition,
        season,
    ) = setup_test_database()

    try:
        now = datetime(
            2024,
            8,
            17,
            12,
            tzinfo=timezone.utc,
        )

        create_match(
            db=db,
            home_team=home_team,
            away_team=away_team,
            competition=competition,
            season=season,
            provider_id=1,
            kickoff_at=now + timedelta(hours=3),
            status="NS",
        )

        create_match(
            db=db,
            home_team=home_team,
            away_team=away_team,
            competition=competition,
            season=season,
            provider_id=2,
            kickoff_at=now + timedelta(hours=1),
            status="NS",
        )

        create_match(
            db=db,
            home_team=home_team,
            away_team=away_team,
            competition=competition,
            season=season,
            provider_id=3,
            kickoff_at=now + timedelta(hours=2),
            status="NS",
        )

        db.commit()

        repository = FeedRepository(db)

        matches = repository.get_upcoming_matches(
            now=now,
        )

        assert [
            match.provider_id
            for match in matches
        ] == [2, 3, 1]

    finally:
        db.close()
        teardown_test_database()


def test_upcoming_matches_respect_limit():
    (
        db,
        home_team,
        away_team,
        competition,
        season,
    ) = setup_test_database()

    try:
        now = datetime(
            2024,
            8,
            17,
            12,
            tzinfo=timezone.utc,
        )

        for provider_id in range(1, 6):
            create_match(
                db=db,
                home_team=home_team,
                away_team=away_team,
                competition=competition,
                season=season,
                provider_id=provider_id,
                kickoff_at=now + timedelta(
                    hours=provider_id
                ),
                status="NS",
            )

        db.commit()

        repository = FeedRepository(db)

        matches = repository.get_upcoming_matches(
            now=now,
            limit=2,
        )

        assert len(matches) == 2

        assert [
            match.provider_id
            for match in matches
        ] == [1, 2]

    finally:
        db.close()
        teardown_test_database()


def test_matches_by_date_return_all_matches_in_window():
    (
        db,
        home_team,
        away_team,
        competition,
        season,
    ) = setup_test_database()

    try:
        start = datetime(
            2024,
            8,
            17,
            tzinfo=timezone.utc,
        )

        create_match(
            db=db,
            home_team=home_team,
            away_team=away_team,
            competition=competition,
            season=season,
            provider_id=1,
            kickoff_at=start + timedelta(hours=2),
            status="NS",
        )

        create_match(
            db=db,
            home_team=home_team,
            away_team=away_team,
            competition=competition,
            season=season,
            provider_id=2,
            kickoff_at=start + timedelta(hours=8),
            status="FT",
        )

        create_match(
            db=db,
            home_team=home_team,
            away_team=away_team,
            competition=competition,
            season=season,
            provider_id=3,
            kickoff_at=start + timedelta(days=1),
            status="NS",
        )

        db.commit()

        repository = FeedRepository(db)

        matches = repository.get_matches_by_date(
            start=start,
            end=start + timedelta(days=1),
        )

        assert len(matches) == 2

        assert [
            match.provider_id
            for match in matches
        ] == [1, 2]

    finally:
        db.close()
        teardown_test_database()