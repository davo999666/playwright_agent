from chains.planner_chain import planner_chain
from tools.tool_registry import get_tool_map
from utils.debug_writer import debug_writer


@debug_writer.debug_wrapper("planner")
async def planner_node(state):
    print("===planner_node===")
    goal = state["goal"]
    start_url = state["start_url"]

    tools = get_tool_map()

    snapshot = await tools["browser_snapshot"].ainvoke({
        "depth": 4
    })

    page_data = "\n".join(str(item) for item in snapshot)

    plan = await planner_chain.ainvoke(
        {
            "goal": goal,
            "start_url": start_url,
            "page_data": page_data,
        }
    )

    return {
        "plan": plan
    }