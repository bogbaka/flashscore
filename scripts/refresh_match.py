from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database.session import SessionLocal
from app.services.live_match import LiveMatchService


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python scripts/refresh_match.py <fixture_id>"
        )

    try:
        fixture_id = int(sys.argv[1])
    except ValueError as error:
        raise SystemExit(
            "Fixture ID must be a number."
        ) from error

    db = SessionLocal()
    service = LiveMatchService(db)

    try:
        match = service.refresh_match(fixture_id)

        print(
            f"Match: {match.home_team.name} "
            f"{match.home_score} - {match.away_score} "
            f"{match.away_team.name}"
        )
        print(f"Status: {match.status}")
        print(f"Events: {len(match.events)}")

    except Exception:
        db.rollback()
        raise

    finally:
        service.close()
        db.close()


if __name__ == "__main__":
    main()