"""LLM tools for backend API endpoints.

This module defines 9 tools that the LLM can call to interact with the backend API.
Each tool is an async function that can be registered with the LLM client.

Tools:
    get_items, get_learners, get_scores, get_pass_rates, get_timeline,
    get_groups, get_top_learners, get_completion_rate, trigger_sync
"""

import logging
from typing import Any

from backend import (
    BackendError,
    check_health,
    fetch_items,
    fetch_pass_rates,
    get_user_friendly_error_message,
)
from config import settings

logger = logging.getLogger(__name__)

# List of all available tools for discovery
__all__ = [
    "get_items",
    "get_learners",
    "get_scores",
    "get_pass_rates",
    "get_timeline",
    "get_groups",
    "get_top_learners",
    "get_completion_rate",
    "trigger_sync",
]


async def get_items() -> list[dict[str, Any]]:
    """Get all items (labs and tasks) from the backend.

    Returns:
        List of all items with their types, titles, and IDs.
    """
    try:
        items = await fetch_items()
        return items
    except BackendError as e:
        return [{"error": get_user_friendly_error_message(e)}]


async def get_learners() -> list[dict[str, Any]]:
    """Get all enrolled learners from the backend.

    Returns:
        List of learners with their IDs and groups.
    """
    url = f"{settings.lms_api_base_url}/learners/"
    headers = {"Authorization": f"Bearer {settings.lms_api_key}"}

    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error fetching learners: {e}")
        return [{"error": str(e)}]


async def get_scores(lab: str) -> list[dict[str, Any]]:
    """Get score distribution for a lab.

    Args:
        lab: Lab identifier (e.g., 'lab-01')

    Returns:
        Score distribution across 4 buckets (0-25, 26-50, 51-75, 76-100).
    """
    url = f"{settings.lms_api_base_url}/analytics/scores"
    params = {"lab": lab}
    headers = {"Authorization": f"Bearer {settings.lms_api_key}"}

    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, params=params, headers=headers, timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error fetching scores: {e}")
        return [{"error": str(e)}]


async def get_pass_rates(lab: str) -> list[dict[str, Any]]:
    """Get per-task pass rates for a lab.

    Args:
        lab: Lab identifier (e.g., 'lab-01')

    Returns:
        List of tasks with their average scores and attempt counts.
    """
    try:
        return await fetch_pass_rates(lab)
    except BackendError as e:
        return [{"error": get_user_friendly_error_message(e)}]


async def get_timeline(lab: str) -> list[dict[str, Any]]:
    """Get submission timeline for a lab.

    Args:
        lab: Lab identifier (e.g., 'lab-01')

    Returns:
        List of dates with submission counts.
    """
    url = f"{settings.lms_api_base_url}/analytics/timeline"
    params = {"lab": lab}
    headers = {"Authorization": f"Bearer {settings.lms_api_key}"}

    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, params=params, headers=headers, timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error fetching timeline: {e}")
        return [{"error": str(e)}]


async def get_groups(lab: str) -> list[dict[str, Any]]:
    """Get per-group performance for a lab.

    Args:
        lab: Lab identifier (e.g., 'lab-01')

    Returns:
        List of groups with their average scores and student counts.
    """
    url = f"{settings.lms_api_base_url}/analytics/groups"
    params = {"lab": lab}
    headers = {"Authorization": f"Bearer {settings.lms_api_key}"}

    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, params=params, headers=headers, timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error fetching groups: {e}")
        return [{"error": str(e)}]


async def get_top_learners(
    lab: str, limit: int = 10
) -> list[dict[str, Any]]:
    """Get top learners by average score for a lab.

    Args:
        lab: Lab identifier (e.g., 'lab-01')
        limit: Number of top learners to return (default: 10)

    Returns:
        List of top learners with their average scores and attempts.
    """
    url = f"{settings.lms_api_base_url}/analytics/top-learners"
    params = {"lab": lab, "limit": limit}
    headers = {"Authorization": f"Bearer {settings.lms_api_key}"}

    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, params=params, headers=headers, timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error fetching top learners: {e}")
        return [{"error": str(e)}]


async def get_completion_rate(lab: str) -> dict[str, Any]:
    """Get completion rate for a lab.

    Args:
        lab: Lab identifier (e.g., 'lab-01')

    Returns:
        Completion rate percentage with passed/total counts.
    """
    url = f"{settings.lms_api_base_url}/analytics/completion-rate"
    params = {"lab": lab}
    headers = {"Authorization": f"Bearer {settings.lms_api_key}"}

    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, params=params, headers=headers, timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error fetching completion rate: {e}")
        return {"error": str(e)}


async def trigger_sync() -> dict[str, Any]:
    """Trigger ETL sync from autochecker API.

    Returns:
        Sync result with new and total record counts.
    """
    url = f"{settings.lms_api_base_url}/pipeline/sync"
    headers = {
        "Authorization": f"Bearer {settings.lms_api_key}",
        "Content-Type": "application/json",
    }

    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, timeout=60.0)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error triggering sync: {e}")
        return {"error": str(e)}
