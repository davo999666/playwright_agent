# tools/tool_registry.py

def get_tools_description(tools):
    """Generate tools description from a list of tools."""
    return "\n".join(
        f"- {tool.name}: {tool.description}"
        for tool in tools
    )


def get_tool_map(tools):
    """Create a mapping of tool names to tools."""
    return {
        tool.name: tool
        for tool in tools
    }