from typing import TypedDict, Annotated, Literal

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    goal: str
    start_url: str
    plan: dict
    navigated: bool
    completed_steps: list[int]
    messages: Annotated[list[BaseMessage], add_messages]
    next_node: Literal["planner", "worker", "tools", "validator", "end"]