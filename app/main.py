from fastapi import FastAPI

from app.api.v1.competitions import router as competitions_router
from app.api.v1.matches import router as matches_router
from app.api.v1.teams import router as teams_router


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


@app.get("/")
def root():
    return {"message": "Football LiveScore API is running!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}