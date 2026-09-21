import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import SUPPORTED_COMPETITIONS
from app.database.session import SessionLocal
from app.services.football_sync import FootballSyncService


def sync_competition(
    slug: str,
    season: int,
) -> None:
    db = SessionLocal()

    try:
        service = FootballSyncService(db)

        result = service.sync_competition(
            slug=slug,
            season=season,
        )

        print(
            f"\nCompetition: "
            f"{result['competition'].name}"
        )

        print(
            f"Season: "
            f"{result['season'].year}"
        )

        print(
            f"Teams synced: "
            f"{len(result['teams'])}"
        )

        print(
            f"Matches synced: "
            f"{len(result['matches'])}"
        )

        print(
            f"Standings synced: "
            f"{len(result['standings'])}"
        )

    finally:
        db.close()


def main() -> None:
    if len(sys.argv) != 3:
        print(
            "Usage: "
            "python scripts/sync_competition.py "
            "<competition|all> <season>"
        )
        return

    slug = sys.argv[1]

    try:
        season = int(sys.argv[2])
    except ValueError:
        print("Season must be a number, e.g. 2026.")
        return

    if slug == "all":
        for competition_slug in SUPPORTED_COMPETITIONS:
            try:
                sync_competition(
                    slug=competition_slug,
                    season=season,
                )
            except Exception as error:
                print(
                    f"\nFailed to sync "
                    f"{competition_slug}: {error}"
                )

        return

    if slug not in SUPPORTED_COMPETITIONS:
        print(
            f"Unsupported competition: {slug}"
        )
        print("Available competitions:")

        for competition_slug in SUPPORTED_COMPETITIONS:
            print(f"  - {competition_slug}")

        return

    sync_competition(
        slug=slug,
        season=season,
    )


if __name__ == "__main__":
    main()