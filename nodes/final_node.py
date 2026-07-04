# nodes/final_node.py

def final_node(state):
    print(f"Final node invoked with state: {state}")
    last_message = state["messages"][-1]

    return {
        "messages": [last_message]
    }