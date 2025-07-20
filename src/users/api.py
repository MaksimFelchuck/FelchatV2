"""API router for user-related endpoints (JSON responses)."""

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response

from src.dependencies import get_user_service
from src.users.schemas import UserCreate, UserLogin, UserRead
from src.users.services import UserService

api_router = APIRouter(prefix="/api/v1/users", tags=["users"])

@api_router.post("/register", response_model=UserRead)
def register(
    user_data: UserCreate, 
    response: Response,
    user_service: UserService = Depends(get_user_service)
):
    """Register a new user via API."""
    try:
        result = user_service.register(user_data)
        
        if result is None:
            raise HTTPException(status_code=400, detail="User already exists")
        response.status_code = 201
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@api_router.post("/login", response_model=UserRead)
def login(
    user_data: UserLogin, 
    response: Response,
    user_service: UserService = Depends(get_user_service)
):
    """Login user via API."""
    user_obj = user_service.login(user_data.username, user_data.password)
    if not user_obj:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    response.set_cookie(key="user_id", value=str(user_obj.id), httponly=True)
    return user_obj

@api_router.post("/logout")
def logout(response: Response):
    """Logout user via API."""
    response.delete_cookie(key="user_id")
    return {"message": "Logged out successfully"}

@api_router.get("/me", response_model=UserRead)
def get_current_user(
    user_id: int = Cookie(None),
    user_service: UserService = Depends(get_user_service)
):
    """Get current user info via API."""
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_obj = user_service.get_user(int(user_id))
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    return user_obj

@api_router.get("/", response_model=list[UserRead])
def list_users(user_service: UserService = Depends(get_user_service)):
    """Get list of all users via API."""
    return user_service.list_users()

@api_router.post("/block/{user_id}")
def block_user(
    user_id: int, 
    current_user_id: int = Cookie(None, alias="user_id"),
    user_service: UserService = Depends(get_user_service)
):
    """Block a user via API."""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_service.block_user(int(current_user_id), user_id)
    return {"message": "User blocked successfully"}

@api_router.delete("/block/{user_id}")
def unblock_user(
    user_id: int, 
    current_user_id: int = Cookie(None, alias="user_id"),
    user_service: UserService = Depends(get_user_service)
):
    """Unblock a user via API."""
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_service.unblock_user(int(current_user_id), user_id)
    return {"message": "User unblocked successfully"} 