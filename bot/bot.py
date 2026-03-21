"""LMS Telegram Bot entry point.

Usage:
    uv run python bot/bot.py           # Run bot in production mode
    uv run python bot/bot.py --test    # Run bot in test mode
    uv run python bot/bot.py --test "/health"  # Test specific command
"""

import argparse
import asyncio
import logging
import sys
from typing import Any

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from config import settings
from handlers import health, help, labs, scores, start

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        nargs="?",
        const=True,
        default=False,
        help="Run bot in test mode. Optionally provide a command to test.",
    )
    return parser.parse_args()


async def handle_message(message: Message, command: str) -> None:
    """Handle incoming message based on command."""
    logger.info(f"Received command: {command}")

    if command == "health":
        response = await health.handle_health()
    elif command == "start":
        response = await start.handle_start()
    elif command == "help":
        response = await help.handle_help()
    elif command == "labs":
        response = await labs.handle_labs()
    elif command.startswith("scores"):
        # Extract lab argument if present
        parts = command.split(maxsplit=1)
        lab = parts[1] if len(parts) > 1 else None
        response = await scores.handle_scores(lab)
    else:
        response = f"Unknown command: {command}. Use /help for available commands."

    await message.answer(response)


async def run_test_mode(command: str | None = None) -> None:
    """Run bot in test mode without Telegram connection.

    Args:
        command: Command to test. If None, runs all handlers.
    """
    logger.info("Running in test mode")

    handlers = {
        "health": health.handle_health,
        "start": start.handle_start,
        "help": help.handle_help,
        "labs": labs.handle_labs,
    }

    if command:
        # Remove leading slash if present
        command = command.lstrip("/")
        
        if command.startswith("scores"):
            # Extract lab argument if present
            parts = command.split(maxsplit=1)
            lab = parts[1] if len(parts) > 1 else None
            logger.info(f"Testing handler: scores with lab={lab}")
            response = await scores.handle_scores(lab)
            print(f"\n{'='*50}")
            print(f"Handler: scores {lab or ''}")
            print(f"Response:\n{response}")
            print(f"{'='*50}\n")
        elif command in handlers:
            logger.info(f"Testing handler: {command}")
            response = await handlers[command]()
            print(f"\n{'='*50}")
            print(f"Handler: {command}")
            print(f"Response:\n{response}")
            print(f"{'='*50}\n")
        else:
            logger.error(f"Unknown command: {command}")
            print(f"Unknown command: {command}")
            print(f"Available commands: {', '.join(list(handlers.keys()) + ['scores <lab>'])}")
    else:
        # Run all handlers
        logger.info("Testing all handlers")
        for name, handler in handlers.items():
            response = await handler()
            print(f"\n{'='*50}")
            print(f"Handler: {name}")
            print(f"Response:\n{response}")
            print(f"{'='*50}\n")
        
        # Test scores handler with a default lab
        logger.info("Testing scores handler with lab-04")
        response = await scores.handle_scores("lab-04")
        print(f"\n{'='*50}")
        print(f"Handler: scores lab-04")
        print(f"Response:\n{response}")
        print(f"{'='*50}\n")

    logger.info("Test mode completed")


async def run_production_mode() -> None:
    """Run bot in production mode with Telegram connection."""
    if not settings.bot_token:
        logger.error("BOT_TOKEN is not set. Please set it in .env.bot.secret")
        sys.exit(1)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def cmd_start(message: Message) -> None:
        """Handle /start command."""
        response = await start.handle_start()
        await message.answer(response)

    @dp.message(Command("health"))
    async def cmd_health(message: Message) -> None:
        """Handle /health command."""
        response = await health.handle_health()
        await message.answer(response)

    @dp.message(Command("help"))
    async def cmd_help(message: Message) -> None:
        """Handle /help command."""
        response = await help.handle_help()
        await message.answer(response)

    @dp.message(Command("labs"))
    async def cmd_labs(message: Message) -> None:
        """Handle /labs command."""
        response = await labs.handle_labs()
        await message.answer(response)

    @dp.message(Command("scores"))
    async def cmd_scores(message: Message) -> None:
        """Handle /scores command with optional lab argument."""
        # Extract lab argument from command text
        lab = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
        response = await scores.handle_scores(lab)
        await message.answer(response)

    @dp.message()
    async def echo_handler(message: Message) -> None:
        """Echo handler for unknown messages."""
        response = "I received your message. Use /help for available commands."
        await message.answer(response)

    logger.info("Bot is starting in production mode...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def main() -> None:
    """Main entry point."""
    args = parse_args()

    if args.test:
        command = args.test if isinstance(args.test, str) else None
        await run_test_mode(command)
    else:
        await run_production_mode()


if __name__ == "__main__":
    asyncio.run(main())
