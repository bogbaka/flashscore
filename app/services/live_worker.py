import threading
import time
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import SessionLocal
from app.integrations.football_api.client import FootballAPIClient
from app.models.match import Match
from app.repositories.feed import LIVE_STATUSES
from app.services.live_match import LiveMatchService
from app.services.match_event_sync import MatchEventSyncService


class LiveSyncWorker:
    def __init__(
        self,
        interval_seconds: int | None = None,
        event_refresh_interval: int | None = None,
        client: FootballAPIClient | None = None,
        stop_event: threading.Event | None = None,
    ):
        self.interval_seconds = (
            interval_seconds
            if interval_seconds is not None
            else settings.live_sync_interval_seconds
        )

        self.event_refresh_interval = (
            event_refresh_interval
            if event_refresh_interval is not None
            else settings.live_event_refresh_interval_seconds
        )

        self.last_event_refresh: dict[int, float] = {}

        self.client = client or FootballAPIClient()
        self._owns_client = client is None

        self.stop_event = stop_event or threading.Event()

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
        event_sync = None
        service = None

        try:
            event_sync = MatchEventSyncService(
                db,
                client=self.client,
            )

            service = LiveMatchService(
                db=db,
                client=self.client,
                event_sync=event_sync,
            )

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
                if self.stop_event.is_set():
                    break

                fixture_id = match.provider_id

                if fixture_id is None:
                    continue

                try:
                    previous_status = match.status

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

                    elif (
                        previous_status in LIVE_STATUSES
                        and refreshed.status not in LIVE_STATUSES
                    ):
                        service.refresh_events(
                            fixture_id
                        )

                        self.last_event_refresh.pop(
                            fixture_id,
                            None
                        )

                        print(
                            f"  Final events refreshed for "
                            f"fixture {fixture_id}."
                        )

                    elif refreshed.status not in LIVE_STATUSES:
                        self.last_event_refresh.pop(
                            fixture_id,
                            None
                        )

                except Exception as error:
                    print(
                        f"  Failed to refresh fixture "
                        f"{fixture_id}: {error}"
                    )

        finally:
            if service is not None:
                service.close()

            if event_sync is not None:
                event_sync.close()

            db.close()

    def stop(self) -> None:
        self.stop_event.set()

    def close(self) -> None:
        self.stop()

        if self._owns_client:
            self.client.close()

    def run_forever(self) -> None:
        print(
            "Live sync worker started. "
            f"Score interval: {self.interval_seconds}s | "
            f"Event interval: {self.event_refresh_interval}s"
        )

        try:
            while not self.stop_event.is_set():
                self.run_once()

                self.stop_event.wait(
                    self.interval_seconds
                )

        finally:
            self.close()


if __name__ == "__main__":
    worker = LiveSyncWorker()
    worker.run_forever()
