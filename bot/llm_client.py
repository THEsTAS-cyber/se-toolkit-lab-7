"""LLM client for intent-based routing with tool calling."""

import json
import logging
import sys
from typing import Any, Callable

import httpx

from config import settings
from tool_schemas import TOOL_SCHEMAS

logger = logging.getLogger(__name__)

# Type alias for tool functions
ToolFunc = Callable[..., Any]


class ToolDefinition:
    """Represents a tool that can be called by the LLM."""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        func: ToolFunc,
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.func = func

    def to_schema(self) -> dict[str, Any]:
        """Convert to OpenAI-compatible tool schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class LLMClient:
    """Client for interacting with OpenAI-compatible LLM APIs."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ):
        self.base_url = (base_url or settings.llm_api_base_url or "").rstrip("/")
        if not self.base_url.endswith("/v1"):
            self.base_url = f"{self.base_url}/v1"
        self.api_key = api_key or settings.llm_api_key or ""
        self.model = model or settings.llm_api_model or "coder-model"
        self.tools: dict[str, ToolDefinition] = {}

    def register_tool(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        func: ToolFunc,
    ) -> None:
        """Register a tool that the LLM can call."""
        self.tools[name] = ToolDefinition(name, description, parameters, func)
        logger.debug(f"Registered tool: {name}")

    def get_tool_schemas(self) -> list[dict[str, Any]]:
        """Get all registered tools in OpenAI-compatible format.
        
        Returns the statically defined TOOL_SCHEMAS from tool_schemas.py.
        """
        return TOOL_SCHEMAS

    async def chat(
        self,
        messages: list[dict[str, Any]],
        use_tools: bool = True,
    ) -> tuple[str, list[tuple[str, dict[str, Any]]]]:
        """Send a chat request to the LLM.

        Args:
            messages: List of conversation messages
            use_tools: Whether to include tool definitions

        Returns:
            Tuple of (response_text, list of (tool_name, tool_args) tuples)
        """
        if not self.base_url or not self.api_key:
            return "LLM is not configured. Please set LLM_API_KEY and LLM_API_BASE_URL.", []

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }

        if use_tools and self.tools:
            payload["tools"] = self.get_tool_schemas()
            payload["tool_choice"] = "auto"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=60.0,
                )
                response.raise_for_status()
                data = response.json()

                # Extract response
                choice = data.get("choices", [{}])[0]
                message = choice.get("message", {})
                content = message.get("content", "") or ""
                tool_calls = message.get("tool_calls", [])

                # Parse tool calls
                parsed_tools: list[tuple[str, dict[str, Any]]] = []
                for tc in tool_calls:
                    func = tc.get("function", {})
                    name = func.get("name", "")
                    args_str = func.get("arguments", "{}")
                    try:
                        args = json.loads(args_str)
                    except json.JSONDecodeError:
                        args = {}
                    parsed_tools.append((name, args))

                return content, parsed_tools

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from LLM: {e}")
            if e.response.status_code == 401:
                return "LLM authentication failed. Token may be expired.", []
            return f"LLM error: HTTP {e.response.status_code}", []
        except httpx.TimeoutException:
            logger.error("LLM request timed out")
            return "LLM request timed out. Please try again.", []
        except Exception as e:
            logger.error(f"Unexpected error calling LLM: {e}")
            return f"LLM error: {e}", []

    async def execute_tool(
        self, name: str, args: dict[str, Any]
    ) -> Any | str:
        """Execute a registered tool.

        Args:
            name: Tool name
            args: Tool arguments

        Returns:
            Tool result or error message
        """
        if name not in self.tools:
            return f"Unknown tool: {name}"

        tool = self.tools[name]
        try:
            result = await tool.func(**args) if args else await tool.func()
            return result
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return f"Error executing {name}: {e}"
