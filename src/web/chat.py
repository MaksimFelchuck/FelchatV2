"""WebSocket chat routes and HTML chat interface."""

import json
from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse

from src.chat.ws_service import ChatWebSocketService
from src.config import settings
from src.dependencies import get_chat_service, get_user_service
from src.logger import websocket_logger
from src.templates_engine import templates
from src.users.services import UserService

router = APIRouter()

def get_current_user(request: Request) -> int | None:
    """
    Get current user ID from cookie. Returns None if not authenticated.
    
    Args:
        request: FastAPI request object
        
    Returns:
        User ID as integer or None if not authenticated
    """
    user_id = request.cookies.get(settings.session_cookie_name)
    if not user_id:
        return None
    try:
        return int(user_id)
    except ValueError:
        websocket_logger.warning(f"Invalid user_id in cookie: {user_id}")
        return None

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
    
    chat_data = await _prepare_chat_data(current_user, other_user_id, user_service, chat_service)
    
    return templates.TemplateResponse("chat.html", {
        "request": request,
        **chat_data
    })


async def _prepare_chat_data(
    current_user: int,
    other_user_id: int,
    user_service: UserService,
    chat_service: ChatWebSocketService
) -> dict:
    """Prepare data for chat page template."""
    history = await chat_service.get_history(current_user, other_user_id)
    user_info = _get_user_info(current_user, other_user_id, user_service)
    is_blocked = user_service.is_blocked(current_user, other_user_id)
    
    return {
        "other_user_id": other_user_id,
        "history": history,
        "current_user": current_user,
        "username": user_info["username"],
        "other_username": user_info["other_username"],
        "is_blocked": is_blocked
    }


def _get_user_info(current_user: int, other_user_id: int, user_service: UserService) -> dict:
    """Get username information for both users."""
    user_obj = user_service.get_user(current_user)
    other_user_obj = user_service.get_user(other_user_id)
    
    return {
        "username": user_obj.username if user_obj else f"id:{current_user}",
        "other_username": other_user_obj.username if other_user_obj else f"id:{other_user_id}"
    }

@router.websocket("/ws/chat/{other_user_id}")
async def chat_ws(
    websocket: WebSocket, 
    other_user_id: int,
    chat_service: ChatWebSocketService = Depends(get_chat_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    WebSocket route for message exchange between users.
    Checks authentication via query parameters, connects user to service, forwards messages.
    """
    await websocket.accept()
    
    user_id = await _authenticate_websocket_user(websocket)
    if not user_id:
        return
    
    await chat_service.connect(user_id, websocket)
    websocket_logger.info(f"WebSocket connection established: user {user_id} -> user {other_user_id}")
    
    try:
        await _handle_websocket_messages(websocket, user_id, other_user_id, chat_service, user_service)
    except WebSocketDisconnect:
        websocket_logger.info(f"WebSocket disconnected: user {user_id}")
    except Exception as e:
        websocket_logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        chat_service.disconnect(user_id, websocket)


async def _authenticate_websocket_user(websocket: WebSocket) -> int | None:
    """Authenticate WebSocket user from query parameters."""
    user_id = websocket.query_params.get("user_id")
    if not user_id:
        await websocket.close(code=4001, reason="Authentication required")
        return None
    
    try:
        return int(user_id)
    except ValueError:
        await websocket.close(code=4002, reason="Invalid user ID")
        return None


async def _handle_websocket_messages(
    websocket: WebSocket,
    user_id: int,
    other_user_id: int,
    chat_service: ChatWebSocketService,
    user_service: UserService
) -> None:
    """Handle incoming WebSocket messages."""
    while True:
        message = await websocket.receive_text()
        if not message.strip():
            continue
            
        await _process_message(websocket, user_id, other_user_id, message, chat_service, user_service)


async def _process_message(
    websocket: WebSocket,
    user_id: int,
    other_user_id: int,
    message: str,
    chat_service: ChatWebSocketService,
    user_service: UserService
) -> None:
    """Process a single WebSocket message."""
    if user_service.is_blocked(user_id, other_user_id):
        await _send_error_message(websocket, "blocked", "Вы заблокированы этим пользователем или заблокировали его")
        return
    
    success = await chat_service.send_personal_message(message, other_user_id, user_id)
    if not success:
        await _send_error_message(websocket, "send_failed", "Не удалось отправить сообщение")


async def _send_error_message(websocket: WebSocket, error_type: str, message: str) -> None:
    """Send error message to WebSocket client."""
    error_data = {"error": error_type, "message": message}
    await websocket.send_text(json.dumps(error_data)) 