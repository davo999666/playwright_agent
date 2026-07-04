# nodes/navigate_node.py

from tools.tool_registry import get_tool_map
from utils.debug_writer import debug_writer


@debug_writer.debug_wrapper("navigate")
async def navigate_node(state):
    print("===navigate_node===")
    import asyncio
    start_url = state["start_url"]

    tools = get_tool_map()

    await tools["browser_navigate"].ainvoke({"url": start_url})
    
    # Add delay to allow user to see the navigation
    await asyncio.sleep(3)
 
    return {
        "navigated": True,
    }