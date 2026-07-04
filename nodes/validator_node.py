# nodes/validator_node.py

from utils.debug_writer import debug_writer


MAX_REPLANS = 2


def _last_tool_error(messages) -> str | None:
    """Return an error string from the most recent ToolMessage, or None."""
    for msg in reversed(messages):
        msg_type = getattr(msg, "type", "")
        if msg_type == "tool":
            content = str(getattr(msg, "content", ""))
            lowered = content.lower()
            if (
                "error" in lowered
                or "failed" in lowered
                or "exception" in lowered
                or "not found" in lowered
            ):
                return content[:500]
            return None
        # Stop scanning once we pass the most recent assistant turn
        if msg_type == "ai":
            return None
    return None


@debug_writer.debug_wrapper("validator")
def validator_node(state):
    """
    Decide what happens after the worker stops calling tools.

    We only reach the validator when the worker returned a message with NO
    tool_calls, which normally means the worker believes the task is done
    (or gave up). The validator's only real job is:

      - If the most recent tool observation was an error AND we still have
        replan budget -> re-plan.
      - Otherwise -> finalize.
    """
    print("===validator_node===")

    messages = state.get("messages", [])
    replan_count = state.get("replan_count", 0)

    if not messages:
        return {"next_node": "final"}

    last = messages[-1]
    last_content = str(getattr(last, "content", "")).strip()

    # If the worker returned an empty answer AND the last tool errored,
    # give the planner one more chance.
    tool_error = _last_tool_error(messages)

    if tool_error and replan_count < MAX_REPLANS and not last_content:
        return {
            "next_node": "planner",
            "last_error": tool_error,
            "replan_count": replan_count + 1,
        }

    # Otherwise wrap up. The final_node will produce the user-facing summary.
    return {
        "next_node": "final",
        "final_answer": last_content or None,
    }
