"""Scores command handler."""

from backend import BackendError, fetch_pass_rates, get_user_friendly_error_message


async def handle_scores(lab: str | None = None) -> str:
    """Handle /scores command.

    Args:
        lab: Lab identifier (e.g., 'lab-04'). If None, returns error message.

    Returns:
        Formatted pass rates for the specified lab.
    """
    if not lab:
        return "Please specify a lab. Usage: /scores <lab-id>\nExample: /scores lab-04"

    try:
        pass_rates = await fetch_pass_rates(lab)

        if not pass_rates:
            return f"No pass rate data available for '{lab}'."

        # Format the response
        response_lines = [f"Pass rates for {lab.replace('-', ' ').title()}:"]

        for rate in pass_rates:
            # Backend returns: task, avg_score, attempts
            task_name = rate.get("task", "Unknown Task")
            avg_score = rate.get("avg_score", 0)  # Already a percentage (0-100)
            attempts = rate.get("attempts", 0)

            # Format percentage with one decimal place
            formatted_rate = f"{avg_score:.1f}%"
            response_lines.append(f"- {task_name}: {formatted_rate} ({attempts} attempts)")

        return "\n".join(response_lines)

    except BackendError as e:
        error_msg = get_user_friendly_error_message(e)
        # Special handling for "not found" errors
        if "not found" in str(e).lower():
            return f"Lab '{lab}' not found. Use /labs to see available labs."
        return error_msg
