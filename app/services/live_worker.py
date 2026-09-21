import time
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.integrations.football_api.client import FootballAPIClient
from app.models.match import Match
from app.repositories.feed import LIVE_STATUSES
from app.services.live_match import LiveMatchService


class LiveSyncWorker:
    def __init__(
        self,
        interval_seconds: int = 60,
        event_refresh_interval: int = 300,
    ):
        self.interval_seconds = interval_seconds
        self.event_refresh_interval = event_refresh_interval
        self.last_event_refresh: dict[int, float] = {}

        self.client = FootballAPIClient()

    def get_live_matches(
        self,
        db: Session,
    ) -> list[Match]:
        return list(
            db.scalars(
                select(Match).where(
                    Match.status.in_(LIVE_STATUSES)
                )
            ).all()
        )

    def should_refresh_events(
        self,
        fixture_id: int,
    ) -> bool:
        last_refresh = self.last_event_refresh.get(
            fixture_id,
            0,
        )

        return (
            time.time() - last_refresh
            >= self.event_refresh_interval
        )

    def run_once(self) -> None:
        db = SessionLocal()

        service = LiveMatchService(
            db=db,
            client=self.client,
        )

        try:
            matches = self.get_live_matches(db)

            if not matches:
                print(
                    f"[{datetime.now(timezone.utc).isoformat()}] "
                    "No live matches."
                )
                return

            print(
                f"[{datetime.now(timezone.utc).isoformat()}] "
                f"Refreshing {len(matches)} live match(es)."
            )

            for match in matches:
                fixture_id = match.provider_id

                if fixture_id is None:
                    continue

                try:
                    refreshed = service.refresh_score(
                        fixture_id
                    )

                    print(
                        f"  {refreshed.home_team.name} "
                        f"{refreshed.home_score} - "
                        f"{refreshed.away_score} "
                        f"{refreshed.away_team.name} "
                        f"[{refreshed.status}]"
                    )

                    if (
                        refreshed.status in LIVE_STATUSES
                        and self.should_refresh_events(
                            fixture_id
                        )
                    ):
                        service.refresh_events(
                            fixture_id
                        )

                        self.last_event_refresh[
                            fixture_id
                        ] = time.time()

                        print(
                            f"  Events refreshed for "
                            f"fixture {fixture_id}."
                        )

                    elif refreshed.status not in LIVE_STATUSES:
                        self.last_event_refresh.pop(
                            fixture_id,
                            None,
                        )

                except Exception as error:
                    print(
                        f"  Failed to refresh fixture "
                        f"{fixture_id}: {error}"
                    )

        finally:
            db.close()

    def close(self) -> None:
        self.client.close()

    def run_forever(self) -> None:
        print(
            "Live sync worker started. "
            f"Score interval: {self.interval_seconds}s | "
            f"Event interval: {self.event_refresh_interval}s"
        )

        try:
            while True:
                self.run_once()
                time.sleep(self.interval_seconds)

        finally:
            self.close()


if __name__ == "__main__":
    worker = LiveSyncWorker(
        interval_seconds=60,
        event_refresh_interval=300,
    )

    worker.run_forever()