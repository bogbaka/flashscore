from datetime import datetime, timedelta

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


@router.get(
    "/",
    response_model=MatchListResponse,
)
def get_matches(
    status: str | None = Query(default=None),
    date: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):
    service = MatchService(db)

    if status:
        matches, total = service.get_matches_by_status(
            status=status,
            page=page,
            limit=limit,
        )

    elif date:
        try:
            start = datetime.fromisoformat(date)
        except ValueError as error:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format",
            ) from error

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

    match = service.get_match(match_id)

    if match is None:
        raise HTTPException(
            status_code=404,
            detail="Match not found",
        )

    return match.events