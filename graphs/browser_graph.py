# graphs/browser_graph.py

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from state import AgentState
from nodes.navigate_node import navigate_node
from nodes.planner_node import planner_node
from nodes.worker_node import worker_node
from nodes.validator_node import validator_node
from nodes.final_node import final_node
from tools.tool_registry import init_tools


class BrowserGraph:
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

        builder.add_conditional_edges(
            "worker",
            self.worker_router,
            {
                "mcp_tools": "mcp_tools",
                "validator": "validator",
            },
        )

        builder.add_edge("mcp_tools", "worker")

        builder.add_conditional_edges(
            "validator",
            self.validator_router,
            {
                "worker": "worker",
                "final": "final",
            },
        )

        builder.add_edge("final", END)

        return builder.compile()

    def worker_router(self, state: AgentState):
        """Route from worker: if tool was called, go to mcp_tools; otherwise go to validator."""
        last_message = state["messages"][-1]

        if getattr(last_message, "tool_calls", None):
            return "mcp_tools"

        return "validator"

    def validator_router(self, state: AgentState):
        """Route from validator: if all steps done, go to final; otherwise back to worker."""
        next_node = state.get("next_node", "worker")

        if next_node == "end":
            return "final"

        return "worker"

    async def run(self, goal: str, start_url: str):
        return await self.app.ainvoke(
            {
                "goal": goal,
                "start_url": start_url,
                "completed_steps": [],
                "messages": [
                    {
                        "role": "user",
                        "content": goal,
                    }
                ],
            }
        )