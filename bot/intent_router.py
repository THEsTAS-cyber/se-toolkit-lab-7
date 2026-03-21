"""Intent-based router for natural language queries."""

import logging
import sys
from typing import Any

from llm_client import LLMClient
from tools import (
    get_completion_rate,
    get_groups,
    get_items,
    get_learners,
    get_pass_rates,
    get_scores,
    get_timeline,
    get_top_learners,
    trigger_sync,
)

logger = logging.getLogger(__name__)

# System prompt for the LLM
SYSTEM_PROMPT = """You are a helpful assistant for a Learning Management System (LMS).
You have access to tools that let you query data about labs, tasks, students, and their performance.

When a user asks a question:
1. First understand what they're asking
2. Use the appropriate tools to get the data
3. Analyze the results and provide a clear, helpful answer

Available tools:
- get_items: Get all labs and tasks. Use this when user asks about available labs or needs to know what exists.
- get_learners: Get enrolled students. Use when user asks about enrollment or student count.
- get_scores: Get score distribution (0-25%, 26-50%, 51-75%, 76-100%) for a specific lab.
- get_pass_rates: Get per-task pass rates and attempt counts for a specific lab.
- get_timeline: Get submission timeline (submissions per day) for a specific lab.
- get_groups: Get per-group performance for a specific lab.
- get_top_learners: Get top N learners by average score for a specific lab.
- get_completion_rate: Get completion rate (% of learners scoring >= 60) for a specific lab.
- trigger_sync: Refresh data from the autochecker system.

Important rules:
- Always call tools to get real data before answering
- If the user doesn't specify a lab, ask them which lab they mean OR call get_items first to see available labs
- For comparisons (e.g., "which lab has the lowest"), you need to call the relevant tool for each lab
- After getting tool results, analyze them and provide a clear summary
- Include specific numbers in your answer (percentages, counts, etc.)
- If you can't find the answer or tools fail, explain what went wrong

Lab IDs are in the format "lab-01", "lab-02", etc.
"""


def debug_log(message: str) -> None:
    """Print debug message to stderr (visible in --test mode)."""
    print(f"[debug] {message}", file=sys.stderr)


def create_llm_client() -> LLMClient:
    """Create and configure LLM client with all tools."""
    client = LLMClient()

    # Register all 9 tools
    client.register_tool(
        name="get_items",
        description="Get list of all labs and tasks. Use to see what labs are available or to get lab IDs.",
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
        },
        func=get_items,
    )

    client.register_tool(
        name="get_learners",
        description="Get list of enrolled learners with their groups. Use to answer questions about enrollment.",
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
        },
        func=get_learners,
    )

    client.register_tool(
        name="get_scores",
        description="Get score distribution (buckets: 0-25%, 26-50%, 51-75%, 76-100%) for a specific lab.",
        parameters={
            "type": "object",
            "properties": {
                "lab": {
                    "type": "string",
                    "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                }
            },
            "required": ["lab"],
        },
        func=get_scores,
    )

    client.register_tool(
        name="get_pass_rates",
        description="Get per-task average scores and attempt counts for a specific lab.",
        parameters={
            "type": "object",
            "properties": {
                "lab": {
                    "type": "string",
                    "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                }
            },
            "required": ["lab"],
        },
        func=get_pass_rates,
    )

    client.register_tool(
        name="get_timeline",
        description="Get submission timeline (submissions per day) for a specific lab.",
        parameters={
            "type": "object",
            "properties": {
                "lab": {
                    "type": "string",
                    "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                }
            },
            "required": ["lab"],
        },
        func=get_timeline,
    )

    client.register_tool(
        name="get_groups",
        description="Get per-group average scores and student counts for a specific lab.",
        parameters={
            "type": "object",
            "properties": {
                "lab": {
                    "type": "string",
                    "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                }
            },
            "required": ["lab"],
        },
        func=get_groups,
    )

    client.register_tool(
        name="get_top_learners",
        description="Get top N learners by average score for a specific lab.",
        parameters={
            "type": "object",
            "properties": {
                "lab": {
                    "type": "string",
                    "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of top learners to return (default: 10)",
                },
            },
            "required": ["lab"],
        },
        func=get_top_learners,
    )

    client.register_tool(
        name="get_completion_rate",
        description="Get completion rate (% of learners scoring >= 60) for a specific lab.",
        parameters={
            "type": "object",
            "properties": {
                "lab": {
                    "type": "string",
                    "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                }
            },
            "required": ["lab"],
        },
        func=get_completion_rate,
    )

    client.register_tool(
        name="trigger_sync",
        description="Trigger ETL sync to refresh data from the autochecker system.",
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
        },
        func=trigger_sync,
    )

    return client


async def route_query(
    user_message: str,
    client: LLMClient | None = None,
    debug: bool = True,
) -> str:
    """Route a natural language query through the LLM.

    Args:
        user_message: The user's message
        client: Optional LLM client (creates one if not provided)
        debug: Whether to print debug logs to stderr

    Returns:
        The final response to send to the user
    """
    if client is None:
        client = create_llm_client()

    # Check if LLM is configured
    if not client.api_key or not client.base_url:
        return "LLM is not configured. Please contact the administrator to set up LLM_API_KEY and LLM_API_BASE_URL."

    # Initialize conversation
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    max_iterations = 10  # Prevent infinite loops
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Call LLM
        if debug:
            debug_log(f"Iteration {iteration}: Calling LLM")

        response_text, tool_calls = await client.chat(messages)

        if debug:
            if tool_calls:
                for tool_name, args in tool_calls:
                    debug_log(f"LLM called tool: {tool_name}({args})")
            else:
                debug_log(f"LLM response (no tools): {response_text[:100]}...")

        # If no tools called, return the response
        if not tool_calls:
            if debug:
                debug_log("No more tool calls, returning final response")
            return response_text or "I'm not sure how to help with that. Try asking about labs, scores, or students."

        # Execute tools and collect results
        tool_results = []
        for tool_name, args in tool_calls:
            if debug:
                debug_log(f"Executing tool: {tool_name}")

            result = await client.execute_tool(tool_name, args)

            if debug:
                result_str = str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
                debug_log(f"Tool {tool_name} result: {result_str}")

            tool_results.append(
                {
                    "role": "tool",
                    "tool_call_id": f"call_{iteration}",
                    "content": str(result),
                }
            )

        # Add assistant message and tool results to conversation
        messages.append(
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": f"call_{iteration}",
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": str(args),
                        },
                    }
                    for tool_name, args in tool_calls
                ],
            }
        )
        messages.extend(tool_results)

        if debug:
            debug_log(f"Feeding {len(tool_results)} tool result(s) back to LLM")

    # Max iterations reached
    return "I'm having trouble processing this request. Please try rephrasing your question."
