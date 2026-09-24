import logging
import threading
from contextlib import asynccontextmanager
from threading import Thread

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
from app.config import settings
from app.integrations.football_api.client import FootballAPIClient
from app.services.live_worker import LiveSyncWorker


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = FootballAPIClient()

    worker = None
    worker_thread = None
    stop_event = None

    app.state.football_api_client = client
    app.state.live_sync_worker = None
    app.state.live_sync_thread = None

    if settings.live_sync_enabled:
        stop_event = threading.Event()

        worker = LiveSyncWorker(
            interval_seconds=settings.live_sync_interval_seconds,
            event_refresh_interval=settings.live_event_refresh_interval_seconds,
            client=client,
            stop_event=stop_event,
        )

        worker_thread = Thread(
            target=worker.run_forever,
            name="football-live-sync",
            daemon=True,
        )

        app.state.live_sync_worker = worker
        app.state.live_sync_thread = worker_thread

        logger.info(
            "Starting football live sync worker. "
            "Score interval: %ss | Event interval: %ss",
            settings.live_sync_interval_seconds,
            settings.live_event_refresh_interval_seconds,
        )

        worker_thread.start()

    else:
        logger.info(
            "Football live sync worker is disabled."
        )

    try:
        yield

    finally:
        if worker is not None:
            logger.info(
                "Stopping football live sync worker."
            )

            worker.stop()

            if worker_thread is not None:
                worker_thread.join(
                    timeout=15
                )

                if worker_thread.is_alive():
                    logger.warning(
                        "Football live sync worker did not stop "
                        "within the shutdown timeout."
                    )

            worker.close()

        client.close()

        logger.info(
            "Football application shutdown complete."
        )


app = FastAPI(
    title="Football LiveScore API",
    lifespan=lifespan,
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
        "status": "healthy",
    }