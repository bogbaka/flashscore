from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.standing import StandingResponse
from app.services.standing import StandingService


router = APIRouter(
    prefix="/standings",
    tags=["Standings"],
)


@router.get(
    "/{competition_id}",
    response_model=list[StandingResponse],
)
def get_standings(
    competition_id: int,
    db: Session = Depends(get_db),
):
    service = StandingService(db)

    return service.get_by_competition(
        competition_id
    )