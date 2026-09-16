from datetime import date, datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends, Query
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
    feed_date: date | None = Query(default=None),
    limit: int = Query(
        default=20,
        ge=1,
        le=50,
    ),
    db: Session = Depends(get_db),
):
    service = FeedService(db)

    selected_date = (
        feed_date
        or datetime.now(timezone.utc).date()
    )

    start = datetime.combine(
        selected_date,
        time.min,
        tzinfo=timezone.utc,
    )

    end = start + timedelta(days=1)

    return service.get_feed(
        start=start,
        end=end,
        limit=limit,
    )