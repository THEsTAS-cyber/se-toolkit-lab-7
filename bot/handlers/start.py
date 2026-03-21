"""Start command handler with inline keyboard buttons."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# List of all keyboard buttons for discovery
KEYBOARD_BUTTONS = [
    ("📊 Check Health", "cmd_health"),
    ("📚 List Labs", "cmd_labs"),
    ("🏆 Top Students", "cmd_top_lab04"),
    ("📈 Pass Rates", "cmd_scores_lab04"),
    ("❓ Help", "cmd_help"),
]


async def handle_start() -> str:
    """Handle /start command.

    Returns:
        Welcome message.
    """
    return (
        "👋 Welcome to LMS Bot!\n\n"
        "I can help you with course information and analytics.\n\n"
        "You can use commands or just ask me questions in plain language!\n\n"
        "Examples:\n"
        "• \"What labs are available?\"\n"
        "• \"Show me scores for lab 4\"\n"
        "• \"Which lab has the lowest pass rate?\"\n"
        "• \"Who are the top 5 students?\"\n\n"
        "Available commands:\n"
        "/health - Check backend status\n"
        "/labs - List available labs\n"
        "/scores <lab> - Show pass rates for a lab\n"
        "/help - Get help message\n"
    )


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Get inline keyboard for /start command.
    
    Returns:
        InlineKeyboardMarkup with buttons for common actions.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Check Health", callback_data="cmd_health"),
            InlineKeyboardButton(text="📚 List Labs", callback_data="cmd_labs"),
        ],
        [
            InlineKeyboardButton(text="🏆 Top Students", callback_data="cmd_top_lab04"),
            InlineKeyboardButton(text="📈 Pass Rates", callback_data="cmd_scores_lab04"),
        ],
        [
            InlineKeyboardButton(text="❓ Help", callback_data="cmd_help"),
        ],
    ])
    return keyboard
