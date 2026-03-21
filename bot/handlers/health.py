"""Health check handler."""


async def handle_health() -> str:
    """Handle health check request.
    
    Returns:
        Health status message.
    """
    return "Bot is healthy and running!"
