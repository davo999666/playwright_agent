# nodes/planner_node.py

from chains.planner_chain import planner_chain
from utils.debug_writer import debug_writer


@debug_writer.debug_wrapper("planner")
async def planner_node(state):
    goal = state["goal"]
    start_url = state["start_url"]

    page_data = state.get("page_data", "")

    plan = await planner_chain.ainvoke(
        {
            "goal": goal,
            "page_data": page_data,
        }
    )

    return {
        "plan": {
            "start_url": start_url,
            **plan,
        }
    }