from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.match_event import MatchEvent
from app.schemas.match_details import MatchDetailsResponse
from app.schemas.match_event import MatchEventResponse
from app.services.match import MatchService


router = APIRouter(
    prefix="/matches",
    tags=["Matches"],
)


@router.get("/")
def get_matches(
    status: str | None = Query(default=None),
    date: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = MatchService(db)

    if status:
        matches, total = service.get_matches_by_status(
            status,
            page,
            limit,
        )

    elif date:
        start = datetime.fromisoformat(date)
        end = start + timedelta(days=1)

        matches, total = service.get_matches_by_date(
            start,
            end,
            page,
            limit,
        )

    else:
        matches, total = service.get_all_matches(
            page,
            limit,
        )

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "matches": matches,
    }


@router.get(
    "/{match_id}/events",
    response_model=list[MatchEventResponse],
)
def get_match_events(
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

    events = (
        db.query(MatchEvent)
        .filter(
            MatchEvent.match_id == match.id
        )
        .order_by(MatchEvent.minute)
        .all()
    )

    return events


@router.get(
    "/{match_id}",
    response_model=MatchDetailsResponse,
)
def get_match(
    match_id: int,
    db: Session = Depends(get_db),
):
    service = MatchService(db)

    match = service.get_match_details(match_id)

    if match is None:
        raise HTTPException(
            status_code=404,
            detail="Match not found",
        )

    return match
