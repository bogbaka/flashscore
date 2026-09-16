from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.competition import CompetitionResponse
from app.schemas.competition_details import (
    CompetitionDetailsResponse,
)
from app.services.competition import CompetitionService


router = APIRouter(
    prefix="/competitions",
    tags=["Competitions"],
)


@router.get(
    "/",
    response_model=list[CompetitionResponse],
)
def get_competitions(
    db: Session = Depends(get_db),
):
    service = CompetitionService(db)

    return service.get_all_competitions()


@router.get(
    "/{competition_id}",
    response_model=CompetitionDetailsResponse,
)
def get_competition(
    competition_id: int,
    db: Session = Depends(get_db),
):
    service = CompetitionService(db)

    competition = service.get_competition_details(
        competition_id
    )

    if competition is None:
        raise HTTPException(
            status_code=404,
            detail="Competition not found",
        )

    return competition