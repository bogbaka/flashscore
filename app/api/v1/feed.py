from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.feed import FeedResponse
from app.services.feed import FeedService


router = APIRouter(
    prefix="/feed",
    tags=["Feed"],
)


@router.get(
    "/",
    response_model=FeedResponse,
)
def get_feed(
    db: Session = Depends(get_db),
):
    service = FeedService(db)

    return service.get_feed()