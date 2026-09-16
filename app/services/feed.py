from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.repositories.feed import FeedRepository


LIVE_STATUSES = [
    "1H",
    "HT",
    "2H",
    "ET",
    "P",
]

FINISHED_STATUSES = [
    "FT",
    "AET",
    "PEN",
]

UPCOMING_STATUSES = [
    "NS",
    "TBD",
]


class FeedService:
    def __init__(self, db: Session):
        self.repository = FeedRepository(db)

    def get_feed(self):
        now = datetime.now(timezone.utc)

        start_of_today = now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        end_of_today = start_of_today + timedelta(days=1)

        live_rows = self.repository.get_matches(
            statuses=LIVE_STATUSES,
        )

        today_rows = self.repository.get_matches(
            start=start_of_today,
            end=end_of_today,
        )

        upcoming_rows = self.repository.get_matches(
            start=end_of_today,
            statuses=UPCOMING_STATUSES,
        )

        finished_rows = self.repository.get_matches(
            start=start_of_today,
            end=end_of_today,
            statuses=FINISHED_STATUSES,
        )

        return {
            "live": self._serialize(live_rows),
            "today": self._serialize(today_rows),
            "upcoming": self._serialize(upcoming_rows),
            "finished": self._serialize(finished_rows),
        }

    def _serialize(self, rows):
        return [
            {
                "id": match.id,
                "kickoff_at": match.kickoff_at,
                "status": match.status,
                "home_score": match.home_score,
                "away_score": match.away_score,
                "home_team": {
                    "id": home_team.id,
                    "name": home_team.name,
                    "short_name": home_team.short_name,
                    "logo_url": home_team.logo_url,
                },
                "away_team": {
                    "id": away_team.id,
                    "name": away_team.name,
                    "short_name": away_team.short_name,
                    "logo_url": away_team.logo_url,
                },
                "competition": {
                    "id": competition.id,
                    "name": competition.name,
                    "country": competition.country,
                    "logo_url": competition.logo_url,
                },
            }
            for (
                match,
                home_team,
                away_team,
                competition,
            ) in rows
        ]