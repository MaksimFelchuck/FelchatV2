"""Web (HTML) routes for user registration, login, profile, and user list."""

from fastapi import APIRouter, Depends, Form, Request, Response, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from src.di.container import Container
from src.templates_engine import templates
from src.users.schemas import UserRead
from src.users.services import UserService

router = APIRouter()

# Create container instance for this module
container = Container()
container.config.env.from_env("ENV", default="prod")
user_service = UserService(repo=container.user_repository())

def get_current_user(request: Request):
    """
    Get current user from cookie. Returns None if not authenticated.
    
    Args:
        request: FastAPI request object
        
    Returns:
        User object or None if not authenticated
    """
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None
    return user_service.get_user(int(user_id))

@router.get("/users/register")
def register_page(request: Request):
    """Render registration page."""
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/users/register")
def register(
    request: Request, 
    username: str = Form(...), 
    email: str = Form(...), 
    password: str = Form(...)
):
    """Handle registration form submission."""
    from src.users.schemas import UserCreate
    try:
        user_data = UserCreate(username=username, email=email, password=password)
    except ValidationError:
        return templates.TemplateResponse(
            "register.html", 
            {"request": request, "error": "Введите корректный email."}
        )
    try:
        result = user_service.register(user_data)
    except Exception as e:
        print(f"DEBUG: Registration error: {e}")  # Debug info
        return templates.TemplateResponse(
            "register.html", 
            {"request": request, "error": f"Ошибка регистрации: {str(e)}"}
        )
    if result is None:
        print("DEBUG: Registration returned None")  # Debug info
        return templates.TemplateResponse(
            "register.html", 
            {"request": request, "error": "Пользователь с таким именем уже существует."}
        )
    print("DEBUG: Registration successful, redirecting to login")  # Debug info
    return RedirectResponse("/users/login", status_code=status.HTTP_302_FOUND)

@router.get("/users/login")
def login_page(request: Request):
    """Render login page."""
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/users/login")
def login(
    request: Request, 
    response: Response, 
    username: str = Form(...), 
    password: str = Form(...)
):
    """Handle login form submission."""
    user_obj = user_service.login(username, password)
    if not user_obj:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Неверные данные"}
        )
    response = RedirectResponse("/users/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="user_id", value=str(user_obj.id), httponly=True)
    return response

@router.post("/users/logout")
def logout(response: Response):
    """Handle logout."""
    response = RedirectResponse("/users/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="user_id")
    return response

@router.get("/users/")
def users_page(request: Request, current_user: UserRead = Depends(get_current_user)):
    """Render user list page."""
    if not current_user:
        return RedirectResponse("/users/login")
    users = user_service.list_users()
    blocked_ids = [
        u.id for u in users if user_service.is_blocked(current_user.id, u.id)
    ]
    return templates.TemplateResponse(
        "users.html", 
        {
            "request": request, 
            "users": users, 
            "current_user": current_user, 
            "blocked_ids": blocked_ids
        }
    )

@router.get("/users/profile")
def profile_page(request: Request, current_user: UserRead = Depends(get_current_user)):
    """Render profile page."""
    if not current_user:
        return RedirectResponse("/users/login")
    return templates.TemplateResponse(
        "profile.html", 
        {"request": request, "user": current_user}
    ) 