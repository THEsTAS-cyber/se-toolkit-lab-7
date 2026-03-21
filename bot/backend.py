"""Backend API client for LMS integration."""

import logging
from typing import Any

import httpx

from config import settings

logger = logging.getLogger(__name__)


class BackendError(Exception):
    """Exception raised for backend API errors."""

    def __init__(self, message: str, original_error: Exception | None = None):
        self.message = message
        self.original_error = original_error
        super().__init__(message)


def get_user_friendly_error_message(error: Exception) -> str:
    """Convert raw exception to user-friendly error message.

    Args:
        error: The original exception.

    Returns:
        User-friendly error message that includes the actual error.
    """
    error_str = str(error).lower()

    if isinstance(error, httpx.ConnectError):
        return f"Backend error: connection refused ({settings.lms_api_base_url}). Check that the services are running."

    if isinstance(error, httpx.TimeoutException):
        return f"Backend error: request timed out ({settings.lms_api_base_url}). The service may be overloaded."

    if isinstance(error, httpx.HTTPStatusError):
        status_code = error.response.status_code
        return f"Backend error: HTTP {status_code} {error.response.reason_phrase}. The backend service may be down."

    if isinstance(error, httpx.RequestError):
        return f"Backend error: {error}. Check your network connection and backend URL."

    # Generic error - still include the actual error message
    return f"Backend error: {error}. Check that the backend is running and accessible."


async def fetch_items() -> list[dict[str, Any]]:
    """Fetch items (labs and tasks) from backend.

    Returns:
        List of items from the backend.

    Raises:
        BackendError: If the backend request fails.
    """
    url = f"{settings.lms_api_base_url}/items/"
    headers = {"Authorization": f"Bearer {settings.lms_api_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching items: {e}")
        raise BackendError(f"HTTP {e.response.status_code} {e.response.reason_phrase}", e)
    except httpx.ConnectError as e:
        logger.error(f"Connection error fetching items: {e}")
        raise BackendError(f"connection refused ({settings.lms_api_base_url})", e)
    except httpx.TimeoutException as e:
        logger.error(f"Timeout fetching items: {e}")
        raise BackendError("request timed out", e)
    except Exception as e:
        logger.error(f"Unexpected error fetching items: {e}")
        raise BackendError(str(e), e)


async def fetch_pass_rates(lab: str) -> list[dict[str, Any]]:
    """Fetch pass rates for a specific lab.

    Args:
        lab: Lab identifier (e.g., 'lab-04').

    Returns:
        List of pass rate data for each task.

    Raises:
        BackendError: If the backend request fails.
    """
    url = f"{settings.lms_api_base_url}/analytics/pass-rates"
    params = {"lab": lab}
    headers = {"Authorization": f"Bearer {settings.lms_api_key}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching pass rates: {e}")
        if e.response.status_code == 404:
            raise BackendError(f"lab '{lab}' not found", e)
        raise BackendError(f"HTTP {e.response.status_code} {e.response.reason_phrase}", e)
    except httpx.ConnectError as e:
        logger.error(f"Connection error fetching pass rates: {e}")
        raise BackendError(f"connection refused ({settings.lms_api_base_url})", e)
    except httpx.TimeoutException as e:
        logger.error(f"Timeout fetching pass rates: {e}")
        raise BackendError("request timed out", e)
    except Exception as e:
        logger.error(f"Unexpected error fetching pass rates: {e}")
        raise BackendError(str(e), e)


async def check_health() -> dict[str, Any]:
    """Check backend health by fetching items.

    Returns:
        Dict with 'healthy' status and 'item_count' if healthy.

    Raises:
        BackendError: If the backend request fails.
    """
    try:
        items = await fetch_items()
        return {"healthy": True, "item_count": len(items)}
    except BackendError as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in health check: {e}")
        raise BackendError(str(e), e)
