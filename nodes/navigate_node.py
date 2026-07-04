# nodes/navigate_node.py

from tools.tool_registry import get_tool_map
from utils.debug_writer import debug_writer


@debug_writer.debug_wrapper("navigate")
async def navigate_node(state):
    print("===navigate_node===")

    start_url = state["start_url"]
    tools = get_tool_map()

    navigate_tool = tools.get("browser_navigate")
    if navigate_tool is None:
        raise RuntimeError("browser_navigate tool is not available")

    await navigate_tool.ainvoke({"url": start_url})

    return {
        "navigated": True,
        "iteration": 0,
        "replan_count": 0,
        "last_error": None,
    }
