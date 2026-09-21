from sqlalchemy import select
from sqlalchemy.orm import Session

from app.integrations.football_api.client import FootballAPIClient
from app.models.match import Match
from app.services.match_event_sync import MatchEventSyncService


LIVE_STATUSES = {"1H", "HT", "2H", "ET", "BT", "P", "LIVE"}


class LiveMatchService:
    def __init__(
        self,
        db: Session,
        client: FootballAPIClient | None = None,
        event_sync: MatchEventSyncService | None = None,
    ):
        self.db = db
        self.client = client or FootballAPIClient()
        self.event_sync = event_sync or MatchEventSyncService(db)

    def refresh_score(self, fixture_id: int) -> Match:
        match = self.db.scalar(
            select(Match).where(
                Match.provider_id == fixture_id
            )
        )

        if match is None:
            raise ValueError(
                "Match must be synced before it can be refreshed."
            )

        data = self.client.get(
            "fixtures",
            {"id": fixture_id},
        )

        fixtures = data.get("response", [])

        if not fixtures:
            raise ValueError(
                "Football provider returned no fixture."
            )

        fixture = fixtures[0]
        goals = fixture.get("goals", {})
        status = fixture.get("fixture", {}).get("status", {})

        match.home_score = goals.get("home") or 0
        match.away_score = goals.get("away") or 0
        match.status = status.get("short", match.status)

        self.db.commit()
        self.db.refresh(match)

        return match

    def refresh_events(self, fixture_id: int) -> list:
        match = self.db.scalar(
            select(Match).where(
                Match.provider_id == fixture_id
            )
        )

        if match is None:
            raise ValueError(
                "Match must be synced before events can be refreshed."
            )

        try:
            events = self.event_sync.sync_events(fixture_id)

            self.db.commit()

            return events

        except Exception:
            self.db.rollback()
            raise

    def refresh_match(
        self,
        fixture_id: int,
        refresh_events: bool = True,
    ) -> Match:
        match = self.refresh_score(fixture_id)

        if refresh_events and match.status in LIVE_STATUSES:
            self.refresh_events(fixture_id)

        return match

    def close(self) -> None:
        self.client.close()
        self.event_sync.close()