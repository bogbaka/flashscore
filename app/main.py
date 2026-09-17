from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.v1.auth import router as auth_router
from app.api.v1.competitions import router as competitions_router
from app.api.v1.favorites import router as favorites_router
from app.api.v1.feed import router as feed_router
from app.api.v1.matches import router as matches_router
from app.api.v1.search import router as search_router
from app.api.v1.standings import router as standings_router
from app.api.v1.teams import router as teams_router


app = FastAPI(
    title="Football LiveScore API"
)


app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)


templates = Jinja2Templates(
    directory="app/templates"
)


app.include_router(
    auth_router,
    prefix="/api/v1",
)

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
    favorites_router,
    prefix="/api/v1",
)


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "Football LiveScore",
        },
    )


@app.get("/standings")
def standings_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="standings.html",
        context={
            "title": "Standings",
        },
    )


@app.get("/matches/{match_id}")
def match_page(
    request: Request,
    match_id: int,
):
    return templates.TemplateResponse(
        request=request,
        name="match.html",
        context={
            "title": "Match Details",
        },
    )


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }