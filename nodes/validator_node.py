# nodes/validator_node.py

from utils.debug_writer import debug_writer


@debug_writer.debug_wrapper("validator")
def validator_node(state):
    """
    Check if all planned steps have been completed.
    If yes, route to final. If no, route back to worker.
    """
    plan = state.get("plan", {})
    steps = plan.get("steps", [])
    completed_steps = state.get("completed_steps", [])

    if not steps:
        # No plan steps means task is done (worker finished on its own)
        return {"next_node": "end"}

    total_step_ids = [step["id"] for step in steps]
    all_completed = all(step_id in completed_steps for step_id in total_step_ids)

    if all_completed:
        return {"next_node": "end"}

    return {"next_node": "worker"}
