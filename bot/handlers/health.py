"""Health check handler."""

from backend import BackendError, check_health, get_user_friendly_error_message


async def handle_health() -> str:
    """Handle health check request.

    Returns:
        Health status message with backend status.
    """
    try:
        result = await check_health()
        if result["healthy"]:
            return f"Backend is healthy. {result['item_count']} items available."
        else:
            return "Backend is not responding."
    except BackendError as e:
        return get_user_friendly_error_message(e)
