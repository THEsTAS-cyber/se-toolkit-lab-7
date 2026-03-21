"""Labs command handler."""

from backend import BackendError, fetch_items, get_user_friendly_error_message


async def handle_labs() -> str:
    """Handle /labs command.

    Returns:
        Formatted list of available labs.
    """
    try:
        items = await fetch_items()

        if not items:
            return "No labs available in the backend."

        # Filter and group labs by type
        labs = []
        for item in items:
            item_type = item.get("type", "")
            if item_type == "lab":
                labs.append(item)

        if not labs:
            return "No labs found in the backend."

        # Format the response
        response_lines = ["Available labs:"]
        for lab in labs:
            lab_name = lab.get("name", "Unknown Lab")
            lab_id = lab.get("id", "unknown")
            response_lines.append(f"- {lab_name}")

        return "\n".join(response_lines)

    except BackendError as e:
        return get_user_friendly_error_message(e)
