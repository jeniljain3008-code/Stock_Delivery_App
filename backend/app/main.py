import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from backend.app.api.v1.routes import router
from backend.app.core.config import get_settings
from backend.app.core.errors import database_unavailable_detail
from backend.app.core.logging import configure_logging

configure_logging()
settings = get_settings()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Smart Delivery Analytics & Swing Trading Platform",
    version="0.1.0",
    description="Delivery-first NSE swing trading analytics API for accumulation detection.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(OperationalError)
async def database_operational_error_handler(_: Request, exc: OperationalError):
    logger.exception("Database connection failed")
    return JSONResponse(status_code=503, content={"detail": database_unavailable_detail(exc)})


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(_: Request, exc: SQLAlchemyError):
    logger.exception("Database operation failed")
    return JSONResponse(
        status_code=500,
        content={
            "detail": {
                "error": "database_error",
                "message": "A database operation failed.",
            }
        },
    )


@app.get("/health")
def health():
    return {"status": "ok"}
