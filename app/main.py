"""
Main Application

Creates a FastAPI instance, connects routers, applies rate limiter, CORS, docs, and startup tasks.
"""

# --------------------------------------------------------------------------------
# IMPORT LIBRARIES

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from slowapi.middleware import SlowAPIMiddleware

from app.config import settings
from app.routers.admin import router as admin_router
from app.routers.public import router as public_router
from app.routers.auth import router as auth_router
from app.services.backup import run_backup
from app.utils.auth.swagger_auth import get_swagger_basic_auth
from app.utils.rate_limit import limiter

# --------------------------------------------------------------------------------
# APPLICATION INSTANCE

app = FastAPI(
    title="Auth API",
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)

# --------------------------------------------------------------------------------
# CONFIGURATION

# Rate Limiter Middleware
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------------------
# INCLUDE ROUTERS

app.include_router(admin_router, prefix="/api/v1/admin")
app.include_router(public_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")


# --------------------------------------------------------------------------------
# DOCUMENTATION ENDPOINTS

@app.get("/docs", include_in_schema=False)
def get_documentation(credentials: str = Depends(get_swagger_basic_auth)):
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Docs",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css"
    )


@app.get("/redoc", include_in_schema=False)
def get_redoc_documentation(credentials: str = Depends(get_swagger_basic_auth)):
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc"
    )


# --------------------------------------------------------------------------------
# PING ENDPOINT

@app.get("/")
def ping():
    return {"message": "Auth API is running"}


# --------------------------------------------------------------------------------
# BACKGROUND SCHEDULER

async def start_scheduler_if_not_running():
    from app.logger import logger, postgres_handler
    postgres_handler.setup()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_backup, "cron", hour=3, minute=0)
    scheduler.start()
    logger.info("Scheduler started on this worker.")
    run_backup()


@app.on_event("startup")
async def startup_event():
    if settings.TESTING:
        return
    await start_scheduler_if_not_running()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
