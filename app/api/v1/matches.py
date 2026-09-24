from datetime import date, datetime, time, timedelta, timezone
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.match import MatchListResponse
from app.schemas.match_details import MatchDetailsResponse
from app.schemas.match_event import MatchEventResponse
from app.services.match import MatchService


router = APIRouter(
    prefix="/matches",
    tags=["Matches"],
)


class MatchStatus(str, Enum):
    SCHEDULED = "scheduled"
    TBD = "TBD"
    NS = "NS"
    FIRST_HALF = "1H"
    HALF_TIME = "HT"
    SECOND_HALF = "2H"
    EXTRA_TIME = "ET"
    BREAK_TIME = "BT"
    PENALTIES = "P"
    LIVE = "LIVE"
    FINISHED = "FT"
    AFTER_EXTRA_TIME = "AET"
    PENALTY_FINISHED = "PEN"
    POSTPONED = "PST"
    CANCELLED = "CANC"
    ABANDONED = "ABD"
    AWARDED = "AWD"
    WALKOVER = "WO"


@router.get(
    "/",
    response_model=MatchListResponse,
)
def get_matches(
    status: MatchStatus | None = Query(
        default=None,
    ),
    match_date: date | None = Query(
        default=None,
        alias="date",
    ),
    page: int = Query(
        default=1,
        ge=1,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):
    if status and match_date:
        raise HTTPException(
            status_code=400,
            detail="Use either status or date, not both",
        )

    service = MatchService(db)

    if status:
        matches, total = service.get_matches_by_status(
            status=status.value,
            page=page,
            limit=limit,
        )

    elif match_date:
        start = datetime.combine(
            match_date,
            time.min,
            tzinfo=timezone.utc,
        )

        end = start + timedelta(days=1)

        matches, total = service.get_matches_by_date(
            start=start,
            end=end,
            page=page,
            limit=limit,
        )

    else:
        matches, total = service.get_all_matches(
            page=page,
            limit=limit,
        )

    return MatchListResponse(
        page=page,
        limit=limit,
        total=total,
        matches=matches,
    )


@router.get(
    "/{match_id}",
    response_model=MatchDetailsResponse,
)
def get_match(
    match_id: int,
    db: Session = Depends(get_db),
):
    service = MatchService(db)

    match = service.get_match_details(
        match_id
    )

    if match is None:
        raise HTTPException(
            status_code=404,
            detail="Match not found",
        )

    return match


@router.get(
    "/{match_id}/events",
    response_model=list[MatchEventResponse],
)
def get_match_events(
    match_id: int,
    db: Session = Depends(get_db),
):
    service = MatchService(db)

    match = service.get_match(
        match_id
    )

    if match is None:
        raise HTTPException(
            status_code=404,
            detail="Match not found",
        )

    return match.events