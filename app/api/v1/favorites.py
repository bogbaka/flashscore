from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.favorite import FavoriteResponse
from app.services.favorite import FavoriteService
from app.database.session import get_db
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"],
)


@router.post(
    "/team/{team_id}",
    response_model=FavoriteResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_team_favorite(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FavoriteService(db)

    try:
        return service.add_team(
            user_id=current_user.id,
            team_id=team_id,
        )
    except ValueError as error:
        if str(error) == "Team not found":
            raise HTTPException(
                status_code=404,
                detail=str(error),
            ) from error

        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error

@router.post(
    "/competition/{competition_id}",
    response_model=FavoriteResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_competition_favorite(
    competition_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FavoriteService(db)

    try:
        return service.add_competition(
            user_id=current_user.id,
            competition_id=competition_id,
        )
    except ValueError as error:
        if str(error) == "Competition not found":
            raise HTTPException(
                status_code=404,
                detail=str(error),
            ) from error

        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error


@router.get(
    "/",
    response_model=list[FavoriteResponse],
)
def list_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FavoriteService(db)

    return service.list_favorites(
        user_id=current_user.id,
    )


@router.delete(
    "/team/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_team_favorite(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FavoriteService(db)

    try:
        service.remove_team(
            user_id=current_user.id,
            team_id=team_id,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error


@router.delete(
    "/competition/{competition_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_competition_favorite(
    competition_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = FavoriteService(db)

    try:
        service.remove_competition(
            user_id=current_user.id,
            competition_id=competition_id,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error