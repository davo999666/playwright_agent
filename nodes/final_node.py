# nodes/final_node.py

from utils.debug_writer import debug_writer


@debug_writer.debug_wrapper("final")
def final_node(state):
    print("===final_node===")
    last_message = state["messages"][-1]

    return {
        "messages": [last_message]
    }