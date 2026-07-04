# nodes/worker_node.py

import asyncio

from chains.worker_chain import create_worker_chain
from tools.tool_registry import get_tools_description


def create_worker_node(tools):
    """Create a worker node function with the provided tools."""
    worker_chain = create_worker_chain(tools)
    tools_description = get_tools_description(tools)
    
    async def worker_node(state):
        print(f"Worker node invoked with state")
        await asyncio.sleep(2)

        response = worker_chain.invoke(
            {
                "goal": state["goal"],
                "start_url": state["start_url"],
                "plan": state.get("plan", {}),
                "tools_description": tools_description,
            }
        )

        return {
            "messages": [response]
        }
    
    return worker_node