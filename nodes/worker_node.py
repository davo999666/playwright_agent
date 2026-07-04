# nodes/worker_node.py

import asyncio

from chains.worker_chain import create_worker_chain
from tools.tool_registry import get_tools, get_tools_description
from utils.debug_writer import debug_writer


@debug_writer.debug_wrapper("worker")
async def worker_node(state):
    print("===worker_node===")
    await asyncio.sleep(2)

    worker_chain = create_worker_chain(get_tools())

    completed_steps = state.get("completed_steps", [])
    navigated = state.get("navigated", False)

    response = worker_chain.invoke(
        {
            "goal": state["goal"],
            "start_url": state["start_url"],
            "plan": state.get("plan", {}),
            "tools_description": get_tools_description(),
            "completed_steps": completed_steps if completed_steps else "None",
            "navigated": str(navigated),
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
        matched_step = False
        for step in steps:
            if step["id"] not in new_completed_steps:
                action = step.get("action", "")
                # Match tool call to plan step action
                if action in tool_name or tool_name in action:
                    new_completed_steps.append(step["id"])
                    matched_step = True
                    break
        
        # If no plan step was matched, check if all plan steps are already completed
        # In this case, the LLM is providing additional actions beyond the plan
        # We should still allow it to continue until it provides a final answer
        if not matched_step:
            all_plan_steps_completed = all(step["id"] in completed_steps for step in steps)
            if all_plan_steps_completed and steps:
                # All plan steps are done, but LLM is still calling tools
                # This is OK - it might be gathering more info to provide final answer
                # Don't add any new step ID, just keep the current completed_steps
                pass
            else:
                # Some plan steps are not completed but we couldn't match the tool
                # This shouldn't happen normally, but if it does, mark the first uncompleted step as done
                for step in steps:
                    if step["id"] not in new_completed_steps:
                        new_completed_steps.append(step["id"])
                        break
    else:
        # No tool calls — worker is providing a final answer, mark all steps done
        new_completed_steps = [step["id"] for step in steps]

    return {
        "messages": [response],
        "completed_steps": new_completed_steps,
    }