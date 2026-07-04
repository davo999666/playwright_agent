# state.py

from typing import TypedDict, Annotated, Literal, Optional

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict, total=False):
    # User input
    goal: str
    start_url: str

    # Runtime state
    plan: dict
    navigated: bool
    iteration: int
    replan_count: int
    last_error: Optional[str]
    final_answer: Optional[str]

    # LLM conversation history (append-only via add_messages)
    messages: Annotated[list[BaseMessage], add_messages]

    # Routing hint set by validator_node
    next_node: Literal["planner", "worker", "final"]
