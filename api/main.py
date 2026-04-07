from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from api.core.database import Base, get_engine
from api.core.settings import get_settings
from api.routers import (
    auth,
    health,
    private_prediction,
    private_user,
)
from api.utils.ml_model import MLModel
from api.utils.set_up_log import get_logger, set_up_logging


def load_model() -> MLModel:
    settings = get_settings()
    return MLModel(
        Path(settings.vectorizer_path).resolve(),
        Path(settings.model_path).resolve(),
    )


def create_app() -> FastAPI:
    """Application factory."""

    settings = get_settings()

    log_config_path = Path(settings.log_config_path).resolve()
    set_up_logging(log_config_path)
    logger = get_logger(settings.log_name)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Application lifecycle manager."""

        logger.info("Application startup")

        logger.info("Database initialization")
        engine = get_engine()
        Base.metadata.create_all(bind=engine)

        try:
            app.state.ml_model = load_model()
            logger.info("Model loaded")
        except Exception:
            logger.exception("Model loading error")
            app.state.ml_model = None

        yield

        logger.info("Application shutdown")

    app = FastAPI(
        title=settings.api_name,
        description="ECF4 - Fake Or Real News",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.include_router(auth.router)
    app.include_router(health.router)
    app.include_router(private_user.router)
    app.include_router(private_prediction.router)

    return app


app = create_app()
