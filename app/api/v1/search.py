from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.search import SearchResponse
from app.services.search import SearchService


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.get(
    "/",
    response_model=SearchResponse,
)
def search(
    q: str = Query(
        min_length=1,
        max_length=100,
    ),
    db: Session = Depends(get_db),
):
    service = SearchService(db)

    return service.search(q)