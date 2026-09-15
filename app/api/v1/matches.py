from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.match import MatchService


router = APIRouter(
    prefix="/matches",
    tags=["Matches"],
)


@router.get("/")
def get_matches(
    status: str | None = Query(default=None),
    date: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    service = MatchService(db)

    if status:
        return service.get_matches_by_status(status)

    if date:
        start = datetime.fromisoformat(date)
        end = start + timedelta(days=1)
        return service.get_matches_by_date(start, end)

    return service.get_all_matches()


@router.get("/{match_id}")
def get_match(
    match_id: int,
    db: Session = Depends(get_db),
):
    service = MatchService(db)
    match = service.get_match(match_id)

    if match is None:
        raise HTTPException(
            status_code=404,
            detail="Match not found",
        )

    return match