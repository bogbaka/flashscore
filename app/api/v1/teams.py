from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.match import MatchListResponse
from app.schemas.team_details import TeamDetailsResponse
from app.schemas.team_list import TeamListResponse
from app.services.team import TeamService


router = APIRouter(
    prefix="/teams",
    tags=["Teams"],
)


@router.get(
    "/",
    response_model=TeamListResponse,
)
def get_teams(
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
    service = TeamService(db)

    teams, total = service.get_all_teams(
        page=page,
        limit=limit,
    )

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "teams": teams,
    }


@router.get(
    "/{team_id}",
    response_model=TeamDetailsResponse,
)
def get_team(
    team_id: int,
    competition_id: int | None = Query(
        default=None,
        ge=1,
    ),
    season_id: int | None = Query(
        default=None,
        ge=1,
    ),
    db: Session = Depends(get_db),
):
    service = TeamService(db)

    team = service.get_team(team_id)

    if team is None:
        raise HTTPException(
            status_code=404,
            detail="Team not found",
        )

    if (
        competition_id is None
        and season_id is None
    ):
        standing = None

    elif (
        competition_id is not None
        and season_id is not None
    ):
        standing = service.get_team_standing(
            team_id=team_id,
            competition_id=competition_id,
            season_id=season_id,
        )

    else:
        raise HTTPException(
            status_code=400,
            detail=(
                "competition_id and season_id "
                "must be provided together"
            ),
        )

    return {
        "id": team.id,
        "name": team.name,
        "short_name": team.short_name,
        "logo_url": team.logo_url,
        "standing": standing,
    }


@router.get(
    "/{team_id}/matches",
    response_model=MatchListResponse,
)
def get_team_matches(
    team_id: int,
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
    service = TeamService(db)

    team = service.get_team(team_id)

    if team is None:
        raise HTTPException(
            status_code=404,
            detail="Team not found",
        )

    matches, total = service.get_team_matches(
        team_id=team_id,
        page=page,
        limit=limit,
    )

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "matches": matches,
    }