# nodes/planner_node.py

import tiktoken

from chains.planner_chain import planner_chain
from tools.tool_registry import get_tool_map
from utils.debug_writer import debug_writer


@debug_writer.debug_wrapper("planner")
async def planner_node(state):
    goal = state["goal"]
    start_url = state["start_url"]

    tools = get_tool_map()

    snapshot = await tools["browser_snapshot"].ainvoke({
        "depth": 4
    })
    snapshot_text = str(snapshot)

    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = len(encoding.encode(snapshot_text))

    print("SNAPSHOT CHARS:", len(snapshot_text))
    print("SNAPSHOT TOKENS:", tokens)


    if isinstance(snapshot, list):
        page_data = "\n".join(str(item) for item in snapshot)
    else:
        page_data = str(snapshot)

    plan = await planner_chain.ainvoke(
        {
            "goal": goal,
            "page_data": page_data,
        }
    )

    return {
        "page_data": page_data,
        "plan": {
            "start_url": start_url,
            **plan,
        },
    }