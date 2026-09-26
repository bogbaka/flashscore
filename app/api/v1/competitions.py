from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.competition import CompetitionListResponse
from app.schemas.competition_details import CompetitionDetailsResponse
from app.schemas.match import MatchListResponse
from app.schemas.standing import StandingResponse
from app.services.competition import CompetitionService
from app.services.standing import StandingService


router = APIRouter(
    prefix="/competitions",
    tags=["Competitions"],
)


@router.get(
    "/",
    response_model=CompetitionListResponse,
)
def get_competitions(
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
    service = CompetitionService(db)

    competitions, total = service.get_all_competitions(
        page=page,
        limit=limit,
    )

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "competitions": competitions,
    }


@router.get(
    "/{competition_id}",
    response_model=CompetitionDetailsResponse,
)
def get_competition(
    competition_id: int,
    db: Session = Depends(get_db),
):
    service = CompetitionService(db)

    competition = service.get_competition(
        competition_id
    )

    if competition is None:
        raise HTTPException(
            status_code=404,
            detail="Competition not found",
        )

    return competition


@router.get(
    "/{competition_id}/matches",
    response_model=MatchListResponse,
)
def get_competition_matches(
    competition_id: int,
    page: int = Query(
        default=1,
        ge=1,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    season: int | None = Query(
        default=None,
        ge=1900,
    ),
    db: Session = Depends(get_db),
):
    service = CompetitionService(db)

    competition = service.get_competition(
        competition_id
    )

    if competition is None:
        raise HTTPException(
            status_code=404,
            detail="Competition not found",
        )

    matches, total = service.get_competition_matches(
        competition_id=competition_id,
        season_year=season,
        page=page,
        limit=limit,
    )

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "matches": matches,
    }


@router.get(
    "/{competition_id}/standings",
    response_model=list[StandingResponse],
)
def get_competition_standings(
    competition_id: int,
    db: Session = Depends(get_db),
):
    competition_service = CompetitionService(db)

    competition = competition_service.get_competition(
        competition_id
    )

    if competition is None:
        raise HTTPException(
            status_code=404,
            detail="Competition not found",
        )

    standing_service = StandingService(db)

    standings = standing_service.get_competition_standings(
        competition_id
    )

    if not standings:
        raise HTTPException(
            status_code=404,
            detail="Standings not found",
        )

    return standings