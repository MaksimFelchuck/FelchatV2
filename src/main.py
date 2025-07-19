"""Main entry point for the FastAPI application."""

from fastapi import FastAPI, Request
import os
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from src.di.container import Container
from src.users.api import api_router as users_api_router
from src.web.chat import router as chat_router
from src.web.users import router as web_users_router

container = Container()
container.config.env.from_env("ENV", default="prod")

app = FastAPI()

# Export container for other modules
__all__ = ["container", "app"]


app.mount(
    "/static", 
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), 
    name="static"
)

@app.get("/")
def root(request: Request):
    """Redirect to appropriate page based on authentication status."""
    user_id = request.cookies.get("user_id")
    if user_id:
        return RedirectResponse("/users/")
    else:
        return RedirectResponse("/users/login")

@app.get("/ping")
def ping():
    """Health check endpoint."""
    return {"status": "ok"}

app.include_router(users_api_router)
app.include_router(web_users_router)
app.include_router(chat_router)
