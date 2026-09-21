from sqlalchemy import select
from sqlalchemy.orm import Session

from app.integrations.football_api.client import FootballAPIClient
from app.models.match import Match
from app.models.match_event import MatchEvent
from app.models.team import Team


class MatchEventSyncService:
    def __init__(self, db: Session):
        self.db = db
        self.client = FootballAPIClient()

    def sync_events(
        self,
        fixture_id: int,
    ) -> list[MatchEvent]:
        match = self.db.scalar(
            select(Match).where(
                Match.provider_id == fixture_id
            )
        )

        if match is None:
            raise ValueError(
                "Match must be synced before events."
            )

        data = self.client.get(
            "fixtures/events",
            {"fixture": fixture_id},
        )

        self.db.query(MatchEvent).filter(
            MatchEvent.match_id == match.id
        ).delete()

        teams = self.db.scalars(
            select(Team)
        ).all()

        teams_by_provider_id = {
            team.provider_id: team
            for team in teams
            if team.provider_id is not None
        }

        events = []

        for item in data.get("response", []):
            team = teams_by_provider_id.get(
                item["team"]["id"]
            )

            player = item.get("player")

            event = MatchEvent(
                match_id=match.id,
                minute=item["time"].get("elapsed"),
                event_type=item.get("type", "Unknown"),
                player_name=(
                    player.get("name")
                    if player
                    else None
                ),
                team_id=team.id if team else None,
                description=item.get("detail"),
            )

            self.db.add(event)
            events.append(event)

        self.db.flush()

        for event in events:
            self.db.refresh(event)

        return events

    def close(self) -> None:
        self.client.close()
