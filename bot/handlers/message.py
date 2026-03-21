"""Natural language message handler with intent routing."""

import logging

from intent_router import create_llm_client, route_query

logger = logging.getLogger(__name__)

# Global LLM client instance
_llm_client = None


def get_llm_client():
    """Get or create the global LLM client."""
    global _llm_client
    if _llm_client is None:
        _llm_client = create_llm_client()
    return _llm_client


async def handle_message(message: str) -> str:
    """Handle a natural language message.

    Args:
        message: The user's message

    Returns:
        Response from the intent router
    """
    client = get_llm_client()
    return await route_query(message, client=client)
