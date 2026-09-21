from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database.session import SessionLocal
from app.services.match_event_sync import MatchEventSyncService


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python scripts/sync_match_events.py <fixture_id>"
        )

    try:
        fixture_id = int(sys.argv[1])
    except ValueError as error:
        raise SystemExit(
            "Fixture ID must be a number."
        ) from error

    db = SessionLocal()
    service = MatchEventSyncService(db)

    try:
        events = service.sync_events(fixture_id)

        print(
            f"Fixture {fixture_id}: "
            f"{len(events)} events synced."
        )

    except Exception:
        db.rollback()
        raise

    finally:
        service.close()
        db.close()


if __name__ == "__main__":
    main()
