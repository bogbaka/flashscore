import sys

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


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: "
            "python scripts/sync_competition.py "
            "<competition|all> <season>"
        )
        return

    slug = sys.argv[1]
    season = int(sys.argv[2])

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
        print(
            "Available competitions:"
        )

        for competition in SUPPORTED_COMPETITIONS:
            print(
                f"  - {competition}"
            )

        return

    sync_competition(
        slug=slug,
        season=season,
    )


if __name__ == "__main__":
    main()