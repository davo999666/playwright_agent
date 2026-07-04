from contextlib import asynccontextmanager
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools


@asynccontextmanager
async def get_mcp_tools():
    """
    Async context manager that maintains a persistent MCP session for the entire
    application lifecycle. The browser stays open until the context exits.
    """
    client = MultiServerMCPClient(
        {
            "playwright": {
                "command": "npx",
                "args": [
                    "@playwright/mcp@latest",
                    "--browser=msedge",
                    "--caps=network,storage,testing,vision,pdf,devtools"
                ],
                "transport": "stdio",
            }
        }
    )

    # Use session context manager to keep the browser alive
    async with client.session("playwright") as session:
        tools = await load_mcp_tools(session)
        
        if not tools:
            raise RuntimeError("No MCP tools were loaded.")
        
        yield tools