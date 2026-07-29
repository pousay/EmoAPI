from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from core.config import config

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{config.RATE_LIMITER_PER_MINUTE}/minute"],
    enabled=config.RATE_LIMITER_ENABLED,
)


def configure_limiter(app: FastAPI):
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={"error": "Too many requests", "detail": str(exc.detail)},
        )


__all__ = ["limiter", "configure_limiter"]
