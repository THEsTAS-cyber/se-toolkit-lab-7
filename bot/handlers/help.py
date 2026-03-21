"""Help command handler."""


async def handle_help() -> str:
    """Handle /help command.

    Returns:
        Help message with available commands.
    """
    return (
        "📚 LMS Bot Help\n\n"
        "I'm here to assist you with course-related questions.\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/health - Check backend status\n"
        "/labs - List available labs\n"
        "/scores <lab> - Show pass rates for a lab\n"
        "/help - Show this help message\n\n"
        "Just send me a message and I'll try to help!"
    )
