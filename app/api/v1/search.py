from fastapi import APIRouter, Depends, HTTPException, Query
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
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
    ),
    db: Session = Depends(get_db),
):
    query = q.strip()

    if not query:
        raise HTTPException(
            status_code=422,
            detail="Search query cannot be empty",
        )

    service = SearchService(db)

    return service.search(
        query=query,
        limit=limit,
    )