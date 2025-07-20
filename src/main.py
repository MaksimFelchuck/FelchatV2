"""Main entry point for the FastAPI application."""

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from pathlib import Path

from src.config import settings
from src.di.container import Container
from src.logger import app_logger
from src.users.api import api_router as users_api_router
from src.web.chat import router as chat_router
from src.web.users import router as web_users_router

container = Container()
container.config.env.from_env("ENV", default=settings.env)


class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response


app = FastAPI(title="Felchat", version="1.0.0")
app.add_middleware(NoCacheMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Export container for other modules
__all__ = ["container", "app"]

# Mount static files
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
def root(request: Request):
    """Redirect to appropriate page based on authentication status."""
    user_id = request.cookies.get(settings.session_cookie_name)
    if user_id:
        app_logger.info(f"Authenticated user {user_id} accessing root")
        return RedirectResponse("/users/")

    app_logger.info("Unauthenticated user accessing root, redirecting to login")
    return RedirectResponse("/users/login")


@app.get("/ping")
def ping():
    """Health check endpoint."""
    return {"status": "ok"}


app.include_router(users_api_router)
app.include_router(web_users_router)
app.include_router(chat_router)
