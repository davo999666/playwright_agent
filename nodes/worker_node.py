# nodes/worker_node.py

import asyncio

from chains.worker_chain import create_worker_chain
from tools.tool_registry import get_tools, get_tools_description
from utils.debug_writer import debug_writer


@debug_writer.debug_wrapper("worker")
async def worker_node(state):
    await asyncio.sleep(2)

    worker_chain = create_worker_chain(get_tools())

    completed_steps = state.get("completed_steps", [])
    navigated = state.get("navigated", False)
    page_data = state.get("page_data", "")

    response = worker_chain.invoke(
        {
            "goal": state["goal"],
            "start_url": state["start_url"],
            "plan": state.get("plan", {}),
            "tools_description": get_tools_description(),
            "completed_steps": completed_steps if completed_steps else "None",
            "navigated": str(navigated),
            "page_data": page_data if page_data else "No page data available yet",
        }
    )
    usage = response.usage_metadata or {}

    # Print token usage using LangChain's built-in usage_metadata
    print(
        f"Tokens | "
        f"input: {usage.get('input_tokens', 0)} | "
        f"output: {usage.get('output_tokens', 0)} | "
        f"total: {usage.get('total_tokens', 0)}"
)

    # Track which plan step was just completed based on the tool call made
    new_completed_steps = list(completed_steps)
    plan = state.get("plan", {})
    steps = plan.get("steps", [])

    if getattr(response, "tool_calls", None):
        # A tool was called — try to match it to a plan step
        tool_name = response.tool_calls[0]["name"]
        for step in steps:
            if step["id"] not in new_completed_steps:
                action = step.get("action", "")
                # Match tool call to plan step action
                if action in tool_name or tool_name in action:
                    new_completed_steps.append(step["id"])
                    break
    else:
        # No tool calls — worker is providing a final answer, mark all steps done
        new_completed_steps = [step["id"] for step in steps]

    return {
        "messages": [response],
        "completed_steps": new_completed_steps,
    }