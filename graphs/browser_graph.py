# graphs/browser_graph.py

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from state import AgentState
from nodes.navigate_node import navigate_node
from nodes.planner_node import planner_node
from nodes.worker_node import worker_node, MAX_WORKER_ITERATIONS
from nodes.validator_node import validator_node
from nodes.final_node import final_node
from tools.tool_registry import init_tools


class BrowserGraph:
    """
    Flow:

        navigate -> planner -> worker
                                 |
              +------------------+------------------+
              | tool_calls present                  | no tool_calls
              v                                     v
           mcp_tools ---> worker (loop)          validator
                                                    |
                              +---------------------+---------------------+
                              | replan (on tool error, budget left)       |
                              v                                           v
                           planner                                      final -> END
    """

    def __init__(self, mcp_tools):
        init_tools(mcp_tools)
        self.mcp_tools = mcp_tools
        self.app = self.graph()

    def graph(self):
        builder = StateGraph(AgentState)

        builder.add_node("navigate", navigate_node)
        builder.add_node("planner", planner_node)
        builder.add_node("worker", worker_node)
        builder.add_node("mcp_tools", ToolNode(self.mcp_tools))
        builder.add_node("validator", validator_node)
        builder.add_node("final", final_node)

        builder.set_entry_point("navigate")

        builder.add_edge("navigate", "planner")
        builder.add_edge("planner", "worker")

        # Worker either calls a tool (loop) or hands off to the validator.
        builder.add_conditional_edges(
            "worker",
            self.worker_router,
            {
                "mcp_tools": "mcp_tools",
                "validator": "validator",
            },
        )

        # After tools run, always come back to the worker so it can observe
        # the result and decide the next step.
        builder.add_edge("mcp_tools", "worker")

        # Validator sets `next_node` explicitly.
        builder.add_conditional_edges(
            "validator",
            self.validator_router,
            {
                "planner": "planner",
                "final": "final",
            },
        )

        builder.add_edge("final", END)

        return builder.compile()

    def worker_router(self, state: AgentState):
        """Route worker output: tool call -> mcp_tools, else -> validator."""
        messages = state.get("messages", [])
        if not messages:
            return "validator"

        # Safety cap: stop the tool loop if the worker has run too many times.
        if state.get("iteration", 0) >= MAX_WORKER_ITERATIONS:
            return "validator"

        last_message = messages[-1]
        if getattr(last_message, "tool_calls", None):
            return "mcp_tools"

        return "validator"

    def validator_router(self, state: AgentState):
        next_node = state.get("next_node", "final")
        if next_node == "planner":
            return "planner"
        return "final"

    async def run(self, goal: str, start_url: str, recursion_limit: int = 60):
        return await self.app.ainvoke(
            {
                "goal": goal,
                "start_url": start_url,
                "navigated": False,
                "iteration": 0,
                "replan_count": 0,
                "last_error": None,
                "messages": [
                    {
                        "role": "user",
                        "content": goal,
                    }
                ],
            },
            config={"recursion_limit": recursion_limit},
        )
