from fastapi import FastAPI
from app.core import settings, configure_logging
from app.api import api_router
from app.db.database import engine, Base
from app.models import Job, Transaction, JobSummary  # noqa: F401 - ensure models are registered

configure_logging()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
    )

    @app.on_event("startup")
    def on_startup():
        # Auto-create all tables if they don't exist
        Base.metadata.create_all(bind=engine)

    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


app = create_app()
