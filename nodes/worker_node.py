# nodes/worker_node.py

import asyncio

from chains.worker_chain import create_worker_chain
from tools.tool_registry import get_tools, get_tools_description
from utils.debug_writer import debug_writer


@debug_writer.debug_wrapper("worker")
async def worker_node(state):
    await asyncio.sleep(2)

    worker_chain = create_worker_chain(get_tools())

    response = worker_chain.invoke(
        {
            "goal": state["goal"],
            "start_url": state["start_url"],
            "plan": state.get("plan", {}),
            "tools_description": get_tools_description(),
        }
    )

    return {
        "messages": [response]
    }