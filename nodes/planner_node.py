# nodes/planner_node.py

from chains.planner_chain import planner_chain
from tools.tool_registry import get_tool_map
from utils.debug_writer import debug_writer


def _snapshot_to_text(snapshot) -> str:
    """Best-effort conversion of an MCP tool response to plain text."""
    if snapshot is None:
        return ""
    if isinstance(snapshot, str):
        return snapshot
    if isinstance(snapshot, list):
        return "\n".join(str(item) for item in snapshot)
    return str(snapshot)


@debug_writer.debug_wrapper("planner")
async def planner_node(state):
    print("===planner_node===")

    goal = state["goal"]
    start_url = state["start_url"]
    last_error = state.get("last_error") or "(none)"

    tools = get_tool_map()
    snapshot_tool = tools.get("browser_snapshot")

    if snapshot_tool is None:
        raise RuntimeError("browser_snapshot tool is not available")

    # browser_snapshot takes no arguments
    snapshot = await snapshot_tool.ainvoke({})
    page_data = _snapshot_to_text(snapshot)

    # Keep the snapshot bounded so we don't blow up the context window.
    if len(page_data) > 8000:
        page_data = page_data[:8000] + "\n...[truncated]"

    try:
        plan = await planner_chain.ainvoke(
            {
                "goal": goal,
                "start_url": start_url,
                "last_error": last_error,
                "page_data": page_data,
            }
        )
    except Exception as e:
        # If JSON parsing fails, fall back to an empty plan so the worker
        # can still try to act using the tool schemas + snapshot.
        print(f"[planner] failed to parse plan: {e}")
        plan = {"steps": []}

    if not isinstance(plan, dict) or "steps" not in plan:
        plan = {"steps": []}

    return {
        "plan": plan,
        # Reset transient tracking every time we (re)plan
        "iteration": 0,
        "last_error": None,
    }
