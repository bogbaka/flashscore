from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.standing import StandingResponse
from app.services.standing import StandingService


router = APIRouter(
    prefix="/standings",
    tags=["Standings"],
)


@router.get(
    "/",
    response_model=list[StandingResponse],
)
def get_standings(
    competition_id: int = Query(
        ...,
        ge=1,
    ),
    db: Session = Depends(get_db),
):
    service = StandingService(db)

    standings = service.get_competition_standings(
        competition_id
    )

    if not standings:
        raise HTTPException(
            status_code=404,
            detail="Standings not found",
        )

    return standings


@router.get(
    "/competition/{competition_id}",
    response_model=list[StandingResponse],
)
def get_competition_standings(
    competition_id: int,
    db: Session = Depends(get_db),
):
    service = StandingService(db)

    standings = service.get_competition_standings(
        competition_id
    )

    if not standings:
        raise HTTPException(
            status_code=404,
            detail="Standings not found",
        )

    return standings


@router.get(
    "/team/{team_id}",
    response_model=StandingResponse,
)
def get_team_standing(
    team_id: int,
    db: Session = Depends(get_db),
):
    service = StandingService(db)

    standing = service.get_team_standing(
        team_id
    )

    if standing is None:
        raise HTTPException(
            status_code=404,
            detail="Standing not found",
        )

    return standing