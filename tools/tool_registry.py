# tools/tool_registry.py

TOOLS = []
TOOLS_DESCRIPTION = ""
TOOL_MAP = {}
TOOLS_NAMES = ""


def init_tools(tools):
    global TOOLS, TOOLS_DESCRIPTION, TOOL_MAP, TOOLS_NAMES

    TOOLS = tools

    TOOLS_DESCRIPTION = "\n".join(
        f"- {tool.name}: {tool.description}"
        for tool in tools
    )

    TOOL_MAP = {
        tool.name: tool
        for tool in tools
    }

    TOOLS_NAMES = ", ".join(
        tool.name
        for tool in tools
    )


def get_tools():
    return TOOLS


def get_tools_description():
    return TOOLS_DESCRIPTION


def get_tool_map():
    return TOOL_MAP


def get_tools_names():
    return TOOLS_NAMES