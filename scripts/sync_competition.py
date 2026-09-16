from app.database.session import SessionLocal
from app.services.football_sync import FootballSyncService


def main():
    db = SessionLocal()

    try:
        service = FootballSyncService(db)

        result = service.sync_competition(
            slug="premier-league",
            season=2024,
        )

        print(
            f"Competition: {result['competition'].name}"
        )
        print(
            f"Teams synced: {len(result['teams'])}"
        )
        print(
            f"Matches synced: {len(result['matches'])}"
        )
        print(
            f"Standings synced: {len(result['standings'])}"
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()