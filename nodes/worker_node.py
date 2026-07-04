# nodes/worker_node.py

from chains.worker_chain import create_worker_chain
from tools.tool_registry import get_tools
from utils.debug_writer import debug_writer


# Absolute hard cap on worker turns per run. Combined with the graph's
# recursion_limit this prevents any possibility of a runaway loop.
MAX_WORKER_ITERATIONS = 20


@debug_writer.debug_wrapper("worker")
async def worker_node(state):
    print("===worker_node===")

    iteration = state.get("iteration", 0) + 1

    worker_chain = create_worker_chain(get_tools())

    # Only pass the tail of the message history to keep the prompt small.
    history = state.get("messages", [])
    trimmed = history[-20:] if len(history) > 20 else history

    response = await worker_chain.ainvoke(
        {
            "goal": state["goal"],
            "start_url": state["start_url"],
            "plan": state.get("plan", {}),
            "navigated": str(state.get("navigated", False)),
            "messages": trimmed,
        }
    )

    usage = getattr(response, "usage_metadata", None) or {}
    print(
        f"[worker iter={iteration}] tokens "
        f"in={usage.get('input_tokens', 0)} "
        f"out={usage.get('output_tokens', 0)} "
        f"total={usage.get('total_tokens', 0)}"
    )

    # If we've hit the safety cap, drop any pending tool calls so the router
    # exits the tool loop and the validator can wrap things up.
    if iteration >= MAX_WORKER_ITERATIONS and getattr(response, "tool_calls", None):
        print(f"[worker] hit iteration cap ({MAX_WORKER_ITERATIONS}); forcing stop")
        try:
            response.tool_calls = []
        except Exception:
            pass
        if not getattr(response, "content", None):
            response.content = (
                "Reached the maximum number of browser actions before finishing."
            )

    return {
        "messages": [response],
        "iteration": iteration,
    }
