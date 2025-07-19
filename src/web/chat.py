"""WebSocket chat routes and HTML chat interface."""

from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse

from src.chat.ws_service import ChatWebSocketService
from src.dependencies import get_chat_service, get_user_service
from src.templates_engine import templates
from src.users.services import UserService

router = APIRouter()

def get_current_user(request: Request):
    """
    Get current user ID from cookie. Returns None if not authenticated.
    
    Args:
        request: FastAPI request object
        
    Returns:
        User ID as integer or None if not authenticated
    """
    user_id = request.cookies.get("user_id")
    if not user_id:
        return None
    return int(user_id)

@router.get("/chat/{other_user_id}")
async def chat_page(
    request: Request, 
    other_user_id: int, 
    current_user: int = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
    chat_service: ChatWebSocketService = Depends(get_chat_service)
):
    """
    Chat page between current user and another user.
    Redirects to login if not authenticated.
    """
    if not current_user:
        return RedirectResponse("/users/login")
    # Get message history from Redis
    history = await chat_service.get_history(current_user, other_user_id)
    # Get usernames
    user_obj = user_service.get_user(current_user)
    other_user_obj = user_service.get_user(other_user_id)
    username = user_obj.username if user_obj else f"id:{current_user}"
    other_username = (
        other_user_obj.username if other_user_obj else f"id:{other_user_id}"
    )
    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "other_user_id": other_user_id,
            "history": history,
            "current_user": current_user,
            "username": username,
            "other_username": other_username
        }
    )

@router.websocket("/ws/chat/{other_user_id}")
async def chat_ws(
    websocket: WebSocket, 
    other_user_id: int,
    chat_service: ChatWebSocketService = Depends(get_chat_service)
):
    """
    WebSocket route for message exchange between users.
    Checks authentication via cookie, connects user to service, forwards messages.
    """
    user_id = websocket.cookies.get("user_id")
    if not user_id:
        await websocket.close()
        return
    user_id = int(user_id)
    await chat_service.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await chat_service.send_personal_message(
                data, to_user_id=other_user_id, from_user_id=user_id
            )
    except WebSocketDisconnect:
        chat_service.disconnect(user_id, websocket) 