# nodes/validator_node.py

from utils.debug_writer import debug_writer


@debug_writer.debug_wrapper("validator")
def validator_node(state):
    print("===validator_node===")

    last = state["messages"][-1]
    content = str(last.content)

    # Tool failed: re-plan with fresh snapshot/refs
    if "### Error" in content or "Error:" in content:
        return {
            "next_node": "planner",
            "last_error": content,
        }

    # Page changed or MCP created new snapshot: refs changed, re-plan
    if "Page URL:" in content or "Snapshot" in content:
        return {
            "next_node": "planner",
            "last_error": None,
        }

    plan = state.get("plan", {})
    steps = plan.get("steps", [])
    completed_steps = state.get("completed_steps", [])

    if not steps:
        return {"next_node": "end"}

    total_step_ids = [step["id"] for step in steps]
    all_completed = all(step_id in completed_steps for step_id in total_step_ids)

    if all_completed:
        return {"next_node": "end"}

    return {"next_node": "worker"}