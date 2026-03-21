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
        "/health - Check backend status\n"
        "/labs - List available labs\n"
        "/scores <lab> - Show pass rates for a lab\n"
        "/help - Get help message\n"
    )
