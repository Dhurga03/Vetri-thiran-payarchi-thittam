from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import settings
from .database import init_db

from .routes.auth import router as auth_router
from .routes.pages import router as pages_router
from .routes.planners import router as planners_router
from .routes.history import router as history_router


BASE_DIR = Path(__file__).resolve().parent


app = FastAPI(
    title="PocketSmart AI",
    description=(
        "Smart Budget & Recommendation Assistant"
    ),
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=settings.CORS_ORIGINS,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


app.mount(
    "/static",
    StaticFiles(
        directory=str(
            BASE_DIR / "static"
        )
    ),
    name="static"
)


app.include_router(
    pages_router
)

app.include_router(
    auth_router,
    prefix="/api"
)

app.include_router(
    planners_router,
    prefix="/api"
)

app.include_router(
    history_router,
    prefix="/api"
)


@app.on_event("startup")
def startup_event():

    init_db()


@app.get("/health")
def health_check():

    return {
        "status": "ok",
        "application": "PocketSmart AI"
    }


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )