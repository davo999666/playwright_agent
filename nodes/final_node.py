# nodes/final_node.py

from langchain_core.messages import AIMessage

from chains.planner_chain import final_chain
from utils.debug_writer import debug_writer


def _format_recent_messages(messages, limit: int = 12) -> str:
    tail = messages[-limit:] if len(messages) > limit else messages
    lines = []
    for msg in tail:
        role = getattr(msg, "type", type(msg).__name__)
        content = str(getattr(msg, "content", ""))
        if len(content) > 800:
            content = content[:800] + "...[truncated]"
        tool_calls = getattr(msg, "tool_calls", None)
        if tool_calls:
            content = f"{content}\n[tool_calls={tool_calls}]"
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


@debug_writer.debug_wrapper("final")
async def final_node(state):
    print("===final_node===")

    goal = state.get("goal", "")
    plan = state.get("plan", {})
    messages = state.get("messages", [])

    try:
        summary = await final_chain.ainvoke(
            {
                "goal": goal,
                "plan": plan,
                "messages": _format_recent_messages(messages),
            }
        )
    except Exception as e:
        print(f"[final] summarization failed: {e}")
        summary = state.get("final_answer") or "Task ended without a clean summary."

    summary = (summary or "").strip()

    print("\n=== FINAL ANSWER ===")
    print(summary)
    print("====================\n")

    return {
        "final_answer": summary,
        "messages": [AIMessage(content=summary)],
    }
