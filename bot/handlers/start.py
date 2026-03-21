"""Start command handler."""


async def handle_start() -> str:
    """Handle /start command.
    
    Returns:
        Welcome message.
    """
    return (
        "👋 Welcome to LMS Bot!\n\n"
        "I can help you with course information and analytics.\n\n"
        "Available commands:\n"
        "/health - Check bot status\n"
        "/help - Get help message\n"
    )
