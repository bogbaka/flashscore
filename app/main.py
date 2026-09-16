from fastapi import FastAPI

from app.api.v1.competitions import router as competitions_router
from app.api.v1.matches import router as matches_router
from app.api.v1.teams import router as teams_router
from app.api.v1.standings import router as standings_router
from app.api.v1.feed import router as feed_router
from app.api.v1.search import router as search_router
from app.api.v1.auth import router as auth_router
from app.integrations.football_api.client import FootballAPIClient


app = FastAPI(title="Football LiveScore API")


app.include_router(
    teams_router,
    prefix="/api/v1",
)

app.include_router(
    competitions_router,
    prefix="/api/v1",
)

app.include_router(
    matches_router,
    prefix="/api/v1",
)
app.include_router(
    standings_router,
    prefix="/api/v1",
)
app.include_router(
    feed_router,
    prefix="/api/v1",
)
app.include_router(
    search_router,
    prefix="/api/v1",
)
app.include_router(
    auth_router,
    prefix="/api/v1",
)

@app.get("/")
def root():
    return {"message": "Football LiveScore API is running!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/api/v1/football/test")
def football_api_test():
    client = FootballAPIClient()

    return client.get(
        "leagues",
        {"country": "England"},
    )