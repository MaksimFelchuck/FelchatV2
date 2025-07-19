"""Web (HTML) routes for user registration, login, profile, and user list."""

from fastapi import APIRouter, Depends, Form, Request, Response, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from src.config import settings
from src.dependencies import get_user_service
from src.logger import user_logger
from src.templates_engine import templates
from src.users.schemas import UserRead
from src.users.services import UserService

router = APIRouter()

def get_current_user(request: Request, user_service: UserService = Depends(get_user_service)) -> UserRead | None:
    """
    Get current user from cookie. Returns None if not authenticated.
    
    Args:
        request: FastAPI request object
        user_service: User service dependency
        
    Returns:
        User object or None if not authenticated
    """
    user_id = request.cookies.get(settings.session_cookie_name)
    if not user_id:
        return None
    
    try:
        return user_service.get_user(int(user_id))
    except ValueError:
        user_logger.warning(f"Invalid user_id in cookie: {user_id}")
        return None

@router.get("/users/register")
def register_page(request: Request):
    """Render registration page."""
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/users/register")
def register(
    request: Request, 
    username: str = Form(...), 
    email: str = Form(...), 
    password: str = Form(...),
    user_service: UserService = Depends(get_user_service)
):
    """Handle registration form submission."""
    from src.users.schemas import UserCreate
    
    try:
        user_data = UserCreate(username=username, email=email, password=password)
    except ValidationError:
        user_logger.warning(f"Invalid registration data: {email}")
        return _render_register_error(request, "Введите корректный email.")
    
    try:
        result = user_service.register(user_data)
    except Exception as e:
        user_logger.error(f"Registration error: {e}")
        return _render_register_error(request, f"Ошибка регистрации: {str(e)}")
    
    if result is None:
        user_logger.warning(f"Registration failed for username: {username}")
        return _render_register_error(request, "Пользователь с таким именем уже существует.")
    
    user_logger.info(f"User registered successfully: {username}")
    return RedirectResponse("/users/login", status_code=status.HTTP_302_FOUND)


def _render_register_error(request: Request, error_message: str):
    """Render registration page with error message."""
    return templates.TemplateResponse(
        "register.html", 
        {"request": request, "error": error_message}
    )

@router.get("/users/login")
def login_page(request: Request):
    """Render login page."""
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/users/login")
def login(
    request: Request, 
    response: Response, 
    username: str = Form(...), 
    password: str = Form(...),
    user_service: UserService = Depends(get_user_service)
):
    """Handle login form submission."""
    user_obj = user_service.login(username, password)
    if not user_obj:
        user_logger.warning(f"Failed login attempt for username: {username}")
        return _render_login_error(request, "Неверные данные")
    
    user_logger.info(f"User logged in successfully: {username} (ID: {user_obj.id})")
    response = RedirectResponse("/users/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key=settings.session_cookie_name, 
        value=str(user_obj.id), 
        httponly=settings.session_cookie_httponly,
        secure=settings.session_cookie_secure
    )
    return response


def _render_login_error(request: Request, error_message: str):
    """Render login page with error message."""
    return templates.TemplateResponse(
        "login.html", 
        {"request": request, "error": error_message}
    )

@router.post("/users/logout")
def logout(response: Response):
    """Handle logout."""
    user_logger.info("User logged out")
    response = RedirectResponse("/users/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key=settings.session_cookie_name)
    return response

@router.get("/users/")
def users_page(
    request: Request, 
    current_user: UserRead = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Render user list page."""
    if not current_user:
        return RedirectResponse("/users/login")
    
    users = user_service.list_users()
    blocked_ids = _get_blocked_user_ids(current_user.id, users, user_service)
    
    user_logger.info(f"User {current_user.username} accessed user list")
    return templates.TemplateResponse(
        "users.html", 
        {
            "request": request, 
            "users": users, 
            "current_user": current_user, 
            "blocked_ids": blocked_ids
        }
    )


def _get_blocked_user_ids(current_user_id: int, users: list[UserRead], user_service: UserService) -> list[int]:
    """Get list of user IDs that are blocked by or blocking the current user."""
    return [u.id for u in users if user_service.is_blocked(current_user_id, u.id)]

@router.get("/users/profile")
def profile_page(request: Request, current_user: UserRead = Depends(get_current_user)):
    """Render profile page."""
    if not current_user:
        return RedirectResponse("/users/login")
    return templates.TemplateResponse(
        "profile.html", 
        {"request": request, "user": current_user}
    )

@router.post("/users/block/{blocker_id}/{blocked_id}")
def block_user(
    request: Request,
    blocker_id: int,
    blocked_id: int,
    current_user: UserRead = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Block a user."""
    if not _validate_user_action(current_user, blocker_id):
        return RedirectResponse("/users/login")
    
    user_service.block_user(blocker_id, blocked_id)
    user_logger.info(f"User {blocker_id} blocked user {blocked_id}")
    return RedirectResponse("/users/", status_code=status.HTTP_302_FOUND)

@router.post("/users/unblock/{blocker_id}/{blocked_id}")
def unblock_user(
    request: Request,
    blocker_id: int,
    blocked_id: int,
    current_user: UserRead = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Unblock a user."""
    if not _validate_user_action(current_user, blocker_id):
        return RedirectResponse("/users/login")
    
    user_service.unblock_user(blocker_id, blocked_id)
    user_logger.info(f"User {blocker_id} unblocked user {blocked_id}")
    return RedirectResponse("/users/", status_code=status.HTTP_302_FOUND)


def _validate_user_action(current_user: UserRead | None, user_id: int) -> bool:
    """Validate that current user can perform action for the given user ID."""
    return current_user is not None and current_user.id == user_id 