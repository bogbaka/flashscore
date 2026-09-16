from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.team import TeamResponse
from app.schemas.team_details import TeamDetailsResponse
from app.services.team import TeamService


router = APIRouter(
    prefix="/teams",
    tags=["Teams"],
)


@router.get(
    "/",
    response_model=list[TeamResponse],
)
def get_teams(
    db: Session = Depends(get_db),
):
    service = TeamService(db)

    return service.get_all_teams()


@router.get(
    "/{team_id}",
    response_model=TeamDetailsResponse,
)
def get_team(
    team_id: int,
    db: Session = Depends(get_db),
):
    service = TeamService(db)
    team = service.get_team_details(team_id)

    if team is None:
        raise HTTPException(
            status_code=404,
            detail="Team not found",
        )

    return team