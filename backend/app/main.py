import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import close_db, init_db
from app.services.redis_client import close_redis
from app.services.ai_client import close_ai_client

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("populi.backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup & shutdown hooks."""
    logger.info("Starting %s v%s (%s)", settings.APP_NAME, settings.APP_VERSION, settings.ENVIRONMENT)
    await init_db()
    logger.info("Database schema OK")
    try:
        yield
    finally:
        await close_ai_client()
        await close_redis()
        await close_db()
        logger.info("Shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Backend API Smart Campus Voting System with Biometric Facial Verification. "
        "Kontrak lengkap: lihat api-contract.md"
    ),
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS — frontend Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "Retry-After"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Attach a traceable request id to every request."""
    request_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex[:8]}"
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# ---------------------------------------------------------------------------
# Error handlers — format mengikuti api-contract.md §4.3 & §7
# ---------------------------------------------------------------------------
STATUS_TO_CODE = {
    status.HTTP_400_BAD_REQUEST: "INVALID_REQUEST",
    status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
    status.HTTP_403_FORBIDDEN: "FORBIDDEN",
    status.HTTP_404_NOT_FOUND: "RESOURCE_NOT_FOUND",
    status.HTTP_405_METHOD_NOT_ALLOWED: "METHOD_NOT_ALLOWED",
    status.HTTP_409_CONFLICT: "CONFLICT",
    status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: "IMAGE_TOO_LARGE",
    status.HTTP_422_UNPROCESSABLE_ENTITY: "VALIDATION_ERROR",
    status.HTTP_429_TOO_MANY_REQUESTS: "RATE_LIMITED",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "INTERNAL_ERROR",
    status.HTTP_502_BAD_GATEWAY: "AI_INVALID_RESPONSE",
    status.HTTP_503_SERVICE_UNAVAILABLE: "AI_SERVICE_UNAVAILABLE",
    status.HTTP_504_GATEWAY_TIMEOUT: "AI_TIMEOUT",
}


def _error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details=None,
    headers: dict | None = None,
) -> JSONResponse:
    error: dict = {"code": code, "message": message}
    if details is not None:
        error["details"] = details
    body = {
        "success": False,
        "error": error,
        "meta": {"request_id": getattr(request.state, "request_id", None)},
    }
    return JSONResponse(status_code=status_code, content=body, headers=headers)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    detail = exc.detail
    code = STATUS_TO_CODE.get(exc.status_code, "ERROR")
    message = "Terjadi kesalahan."
    details = None

    if isinstance(detail, dict):
        code = detail.get("code", code)
        message = detail.get("message", message)
        details = detail.get("details")
    elif isinstance(detail, str):
        message = detail

    return _error_response(
        request, exc.status_code, code, message, details, getattr(exc, "headers", None)
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = [
        {
            "field": ".".join(str(loc) for loc in err.get("loc", []) if loc != "body"),
            "message": err.get("msg", "Invalid value"),
        }
        for err in exc.errors()
    ]
    return _error_response(
        request,
        status.HTTP_400_BAD_REQUEST,
        "VALIDATION_ERROR",
        "Data yang dikirim tidak valid.",
        details,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return _error_response(
        request,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "INTERNAL_ERROR",
        "Kesalahan internal server.",
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Health"], summary="Health check")
async def health():
    return {
        "status": "healthy",
        "service": "populi-backend",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


app.include_router(api_router)


__all__ = ["app"]
