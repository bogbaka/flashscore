from sqlalchemy.orm import Session

from app.integrations.football_api.client import FootballAPIClient
from app.models.match import Match
from app.models.match_event import MatchEvent
from app.models.team import Team


class MatchEventSyncService:
    def __init__(self, db: Session):
        self.db = db
        self.client = FootballAPIClient()

    def sync_events(self, fixture_id: int) -> list[MatchEvent]:
        match = (
            self.db.query(Match)
            .filter(Match.provider_id == fixture_id)
            .first()
        )

        if match is None:
            raise ValueError("Match must be synced before events.")

        data = self.client.get(
            "fixtures/events",
            {"fixture": fixture_id},
        )

        self.db.query(MatchEvent).filter(
            MatchEvent.match_id == match.id
        ).delete()

        events = []

        for item in data["response"]:
            team = (
                self.db.query(Team)
                .filter(
                    Team.provider_id == item["team"]["id"]
                )
                .first()
            )

            event = MatchEvent(
                match_id=match.id,
                minute=item["time"]["elapsed"],
                event_type=item["type"],
                player_name=(
                    item["player"]["name"]
                    if item.get("player")
                    else None
                ),
                team_id=team.id if team else None,
                description=item.get("detail"),
            )

            self.db.add(event)
            events.append(event)

        self.db.commit()

        for event in events:
            self.db.refresh(event)

        return events