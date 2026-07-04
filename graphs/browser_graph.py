# graphs/browser_graph.py

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from state import AgentState
from nodes.planner_node import planner_node
from nodes.worker_node import worker_node
from nodes.final_node import final_node
from tools.tool_registry import init_tools


class BrowserGraph:
    def __init__(self, mcp_tools):
        init_tools(mcp_tools)
        self.mcp_tools = mcp_tools
        self.app = self.graph()

    def graph(self):
        builder = StateGraph(AgentState)


        builder.add_node("planner", planner_node)
        builder.add_node("worker", worker_node)
        builder.add_node("mcp_tools", ToolNode(self.mcp_tools))
        builder.add_node("final", final_node)

        builder.set_entry_point("planner")

        builder.add_edge("planner", "worker")

        builder.add_conditional_edges(
            "worker",
            self.router,
            {
                "mcp_tools": "mcp_tools",
                "final": "final",
            },
        )

        builder.add_edge("mcp_tools", "worker")
        builder.add_edge("final", END)

        return builder.compile()

    def router(self, state: AgentState):
        last_message = state["messages"][-1]

        if getattr(last_message, "tool_calls", None):
            return "mcp_tools"

        return "final"

    async def run(self, goal: str, start_url: str):
        return await self.app.ainvoke(
            {
                "goal": goal,
                "start_url": start_url,
                "messages": [
                    {
                        "role": "user",
                        "content": goal,
                    }
                ],
            }
        )