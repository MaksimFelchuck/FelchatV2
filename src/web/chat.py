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


@router.get("/chat")
async def chat_page(
    request: Request,
    current_user: int = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
    chat_service: ChatWebSocketService = Depends(get_chat_service),
):
    """
    Chat page between current user and another user.
    Redirects to login if not authenticated.
    """
    if not current_user:
        return RedirectResponse("/users/login")

    # Get other user ID from query parameter
    other_user_id = request.query_params.get("user")
    if not other_user_id:
        # Redirect to users page if no user specified
        return RedirectResponse("/users")

    try:
        other_user_id = int(other_user_id)
    except ValueError:
        return RedirectResponse("/users")

    chat_data = await _prepare_chat_data(
        current_user, other_user_id, user_service, chat_service
    )

    # Debug: print chat data
    websocket_logger.info(
        f"Chat data for user {current_user} -> {other_user_id}: {chat_data}"
    )

    return templates.TemplateResponse("chat.html", {"request": request, **chat_data})


async def _prepare_chat_data(
    current_user: int,
    other_user_id: int,
    user_service: UserService,
    chat_service: ChatWebSocketService,
) -> dict:
    """Prepare data for chat page template."""
    history = await chat_service.get_history(current_user, other_user_id)
    user_info = _get_user_info(current_user, other_user_id, user_service)
    is_blocked = user_service.is_blocked(current_user, other_user_id)

    # Check who blocked whom
    block_info = user_service.who_blocked_whom(current_user, other_user_id)
    is_blocker = False
    is_blocked_user = False

    if block_info:
        blocker_id, blocked_id = block_info
        is_blocker = blocker_id == current_user
        is_blocked_user = blocked_id == current_user

    # Get all users for sidebar - use simple dictionaries
    db_users = user_service.repo.list_users()
    users = []
    blocked_ids = []
    for u in db_users:
        users.append(
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "created_at": u.created_at,
            }
        )
        if user_service.is_blocked(current_user, u.id):
            blocked_ids.append(u.id)

    # Get online users from chat service
    online_users = chat_service.get_online_users()

    # Get current user object for detailed info
    current_user_obj = user_service.repo.get_user_by_id(current_user)

    return {
        "other_user_id": other_user_id,
        "current_user_id": current_user,
        "history": history,
        "current_user": current_user,
        "username": user_info["username"],
        "other_username": user_info["other_username"],
        "email": current_user_obj.email if current_user_obj else "",
        "is_blocked": is_blocked,
        "is_blocker": is_blocker,
        "is_blocked_user": is_blocked_user,
        "users": users,
        "blocked_ids": blocked_ids,
        "online_users": online_users,
    }


def _get_user_info(
    current_user: int, other_user_id: int, user_service: UserService
) -> dict:
    """Get username information for both users."""
    user_obj = user_service.repo.get_user_by_id(current_user)
    other_user_obj = user_service.repo.get_user_by_id(other_user_id)

    return {
        "username": user_obj.username if user_obj else f"id:{current_user}",
        "other_username": (
            other_user_obj.username if other_user_obj else f"id:{other_user_id}"
        ),
    }


@router.websocket("/ws/chat")
async def chat_ws(
    websocket: WebSocket,
    chat_service: ChatWebSocketService = Depends(get_chat_service),
    user_service: UserService = Depends(get_user_service),
):
    """
    WebSocket route for message exchange between users.
    Checks authentication via query parameters, connects user to service, forwards messages.
    """
    # Check authentication before accepting connection
    user_id = await _authenticate_websocket_user(websocket)
    if not user_id:
        return

    # Accept connection only after successful authentication
    await websocket.accept()
    websocket_logger.info(f"WebSocket connection accepted for user {user_id}")

    # Get other user ID from query parameter
    other_user_id = websocket.query_params.get("other_user")
    if not other_user_id:
        await websocket.close(code=4003, reason="Other user ID required")
        return

    try:
        other_user_id = int(other_user_id)
    except ValueError:
        await websocket.close(code=4004, reason="Invalid other user ID")
        return

    await chat_service.connect(user_id, websocket)
    websocket_logger.info(
        f"WebSocket connection established: user {user_id} -> user {other_user_id}"
    )

    try:
        await _handle_websocket_messages(
            websocket, user_id, other_user_id, chat_service, user_service
        )
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
    user_service: UserService,
) -> None:
    """Handle incoming WebSocket messages."""
    while True:
        message = await websocket.receive_text()
        if not message.strip():
            continue

        await _process_message(
            websocket, user_id, other_user_id, message, chat_service, user_service
        )


async def _process_message(
    websocket: WebSocket,
    user_id: int,
    other_user_id: int,
    message: str,
    chat_service: ChatWebSocketService,
    user_service: UserService,
) -> None:
    """Process a single WebSocket message."""
    if user_service.is_blocked(user_id, other_user_id):
        await _send_error_message(
            websocket,
            "blocked",
            "Вы заблокированы этим пользователем или заблокировали его",
        )
        return

    success = await chat_service.send_personal_message(message, other_user_id, user_id)
    if not success:
        await _send_error_message(
            websocket, "send_failed", "Не удалось отправить сообщение"
        )


async def _send_error_message(
    websocket: WebSocket, error_type: str, message: str
) -> None:
    """Send error message to WebSocket client."""
    error_data = {"error": error_type, "message": message}
    await websocket.send_text(json.dumps(error_data))


@router.get("/chat/history")
async def get_chat_history(
    request: Request,
    current_user: int = Depends(get_current_user),
    chat_service: ChatWebSocketService = Depends(get_chat_service),
):
    """Get chat history between current user and another user."""
    if not current_user:
        return {"error": "Unauthorized"}, 401

    # Get other user ID from query parameter
    other_user_id = request.query_params.get("user")
    if not other_user_id:
        return {"error": "User ID required"}, 400

    try:
        other_user_id = int(other_user_id)
    except ValueError:
        return {"error": "Invalid user ID"}, 400

    try:
        history = await chat_service.get_history(current_user, other_user_id)
        return history
    except Exception as e:
        websocket_logger.error(f"Error getting chat history: {e}")
        return {"error": "Failed to load chat history"}, 500
