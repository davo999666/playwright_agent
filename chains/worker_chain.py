# chains/worker_chain.py

from llm.model import model
from prompts.worker_prompt import worker_prompt


def create_worker_chain(tools):
    """Create a worker chain with the provided tools."""
    return worker_prompt | model.bind_tools(tools)