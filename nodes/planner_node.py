# nodes/planner_node.py

async def planner_node(state):
    print(f"Planner node invoked with state:")
    goal = state["goal"]
    start_url = state["start_url"]

    plan = {
        "start_url": start_url,
        "steps": [
            "Open the start URL",
            "Use browser tools to inspect the page",
            "Take a screenshot",
            "Explain the page content",
        ],
    }

    return {
        "plan": plan
    }