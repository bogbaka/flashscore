from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import SUPPORTED_COMPETITIONS
from app.integrations.football_api.client import FootballAPIClient
from app.models.match import Match
from app.models.season import Season
from app.services.competition_sync import CompetitionSyncService
from app.services.match_event_sync import MatchEventSyncService
from app.services.match_sync import MatchSyncService
from app.services.standing_sync import StandingSyncService
from app.services.team_sync import TeamSyncService


class FootballSyncService:
    def __init__(
        self,
        db: Session,
        client: FootballAPIClient | None = None,
    ):
        self.db = db
        self.client = client or FootballAPIClient()
        self._owns_client = client is None

        self.competition_sync = CompetitionSyncService(
            db,
            football_api=self.client,
        )

        self.team_sync = TeamSyncService(
            db,
            client=self.client,
        )

        self.match_sync = MatchSyncService(
            db,
            client=self.client,
        )

        self.match_event_sync = MatchEventSyncService(
            db,
            client=self.client,
        )

        self.standing_sync = StandingSyncService(
            db,
            client=self.client,
        )

    def get_or_create_season(
        self,
        competition_id: int,
        year: int,
    ) -> Season:
        season = self.db.scalar(
            select(Season).where(
                Season.competition_id == competition_id,
                Season.year == year,
            )
        )

        if season is None:
            season = Season(
                competition_id=competition_id,
                year=year,
            )

            self.db.add(season)
            self.db.flush()

        return season

    def sync_competition(
        self,
        slug: str,
        season: int,
    ) -> dict:
        competition_config = SUPPORTED_COMPETITIONS.get(slug)

        if competition_config is None:
            raise ValueError(
                f"Unsupported competition: {slug}"
            )

        league_id = competition_config["provider_id"]

        try:
            competition = (
                self.competition_sync.sync_competition(
                    slug
                )
            )

            season_record = self.get_or_create_season(
                competition_id=competition.id,
                year=season,
            )

            teams = self.team_sync.sync_teams(
                league_id=league_id,
                season=season,
            )

            matches = self.match_sync.sync_matches(
                league_id=league_id,
                season=season,
                season_id=season_record.id,
            )

            standings = self.standing_sync.sync_standings(
                league_id=league_id,
                season=season,
                season_id=season_record.id,
            )

            self.db.commit()

            return {
                "competition": competition,
                "season": season_record,
                "teams": teams,
                "matches": matches,
                "standings": standings,
            }

        except Exception:
            self.db.rollback()
            raise

    def sync_match_events(
        self,
        fixture_id: int,
    ) -> list:
        match = self.db.scalar(
            select(Match).where(
                Match.provider_id == fixture_id
            )
        )

        if match is None:
            raise ValueError(
                "Match must be synced before events."
            )

        try:
            events = self.match_event_sync.sync_events(
                fixture_id
            )

            self.db.commit()

            return events

        except Exception:
            self.db.rollback()
            raise

    def close(self) -> None:
        if self._owns_client:
            self.client.close()